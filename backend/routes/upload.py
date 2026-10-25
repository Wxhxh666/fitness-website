"""
文件上传

安全要点：
1. 只信任文件内容，不信任扩展名（按 magic bytes 判断真实类型）；
2. 图片一律用 Pillow 解码后重新编码，顺带剥掉 EXIF（GPS 定位等隐私）；
3. 按用户 + 日期分目录存放，同时作为每日上传配额的计算依据；
4. 视频只做签名与体积校验（重编码代价太大，生产环境建议走对象存储 + 异步转码）。
"""
import os
import uuid
from datetime import date

from flask import current_app, jsonify, request

from utils.auth import require_auth

from . import upload_bp

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
    PIL_AVAILABLE = True
except ImportError:  # 没装 Pillow 时退化为“签名校验 + 原样落盘”，不会 500
    Image = ImageOps = None
    UnidentifiedImageError = Exception
    PIL_AVAILABLE = False

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi", "mkv"}

# Pillow 重编码后统一输出的格式与扩展名
PIL_FORMAT = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}

# 图片最长边上限，超过则等比缩小（避免上传 8000px 的巨图拖垮列表页）
MAX_IMAGE_EDGE = 4096


def _sniff_image(head: bytes):
    if head.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "gif"
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


def _sniff_video(head: bytes):
    if len(head) >= 12 and head[4:8] == b"ftyp":
        return "mp4"          # mp4 / mov 同属 ISO BMFF，靠 ftyp 识别
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"         # webm / mkv 同属 Matroska
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"AVI ":
        return "avi"
    return None


def _save_dir(user_id: int) -> str:
    day = date.today().strftime("%Y%m%d")
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "static", "uploads", str(user_id), day,
    )
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path


def _reencode_image(file, dest_path: str):
    """
    用 Pillow 解码 → 重新编码落盘。
    好处：损坏文件会被拒绝、图片炸弹受像素上限保护、EXIF/ICC 中的隐私信息被剥离。
    返回实际保存的扩展名。
    """
    file.stream.seek(0)
    try:
        img = Image.open(file.stream)
        img.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("图片文件损坏或不是受支持的图片格式") from exc

    fmt = (img.format or "").upper()
    if fmt not in PIL_FORMAT:
        raise ValueError("仅支持 JPEG / PNG / GIF / WEBP 图片")

    # 按 EXIF 方向自动转正，避免手机上拍的照片横躺
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:  # noqa: BLE001 - EXIF 异常不应阻断上传
        pass

    # 超大图等比缩小
    if max(img.size) > MAX_IMAGE_EDGE:
        img.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.LANCZOS)

    ext = PIL_FORMAT[fmt]
    save_kwargs = {}
    if fmt == "JPEG":
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        save_kwargs = {"quality": 88, "optimize": True, "progressive": True}
    elif fmt == "PNG":
        save_kwargs = {"optimize": True}
    elif fmt == "WEBP":
        save_kwargs = {"quality": 88, "method": 4}
    elif fmt == "GIF" and getattr(img, "is_animated", False):
        # 动图需要 save_all 才能保留全部帧
        save_kwargs = {"save_all": True}

    # 注意：不带 exif 参数保存，等于丢弃原始 EXIF（含 GPS）
    img.save(dest_path, format=fmt, **save_kwargs)
    return ext


@upload_bp.route("/upload", methods=["POST"])
@require_auth
def upload_file(user):
    if "file" not in request.files:
        return jsonify(code=400, msg="未选择文件"), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify(code=400, msg="文件名为空"), 400

    is_video = request.form.get("type") == "video"
    max_size = int(current_app.config.get(
        "UPLOAD_VIDEO_MAX_BYTES" if is_video else "UPLOAD_IMAGE_MAX_BYTES"
    ))
    size_label = f"{max_size / 1024 / 1024:.0f}MB"

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size == 0:
        return jsonify(code=400, msg="文件为空"), 400
    if size > max_size:
        return jsonify(code=400, msg=f"文件大小不能超过 {size_label}"), 400

    head = file.stream.read(32)
    file.stream.seek(0)

    target_dir = _save_dir(user.id)
    quota = int(current_app.config.get("UPLOAD_DAILY_QUOTA", 50))
    if len(os.listdir(target_dir)) >= quota:
        return jsonify(code=429, msg=f"今日上传次数已达上限（{quota} 次），请明天再试"), 429

    if is_video:
        real_ext = _sniff_video(head)
        if real_ext is None:
            return jsonify(code=400, msg="不是受支持的视频文件（mp4/webm/mov/avi/mkv）"), 400
        filename = f"{uuid.uuid4().hex}.{real_ext}"
        dest = os.path.join(target_dir, filename)
        file.stream.seek(0)
        file.save(dest)
    else:
        real_ext = _sniff_image(head)
        if real_ext is None:
            return jsonify(code=400, msg="不是受支持的图片文件（jpg/png/gif/webp）"), 400
        filename = f"{uuid.uuid4().hex}.{real_ext}"
        dest = os.path.join(target_dir, filename)
        if not PIL_AVAILABLE:
            # 没装 Pillow：至少已完成签名校验，原样落盘（推荐安装 Pillow 以剥离 EXIF）
            current_app.logger.warning("[upload] 未安装 Pillow，图片未做重编码与 EXIF 剥离")
            file.stream.seek(0)
            file.save(dest)
            return jsonify(code=0, msg="上传成功", data={
                "url": f"/static/uploads/{user.id}/{os.path.basename(target_dir)}/{filename}",
                "size": os.path.getsize(dest),
            })
        try:
            saved_ext = _reencode_image(file, dest)
        except ValueError as exc:
            return jsonify(code=400, msg=str(exc)), 400
        except Exception:  # noqa: BLE001 - Pillow 内部异常统一按坏文件处理
            current_app.logger.exception("[upload] 图片处理失败")
            return jsonify(code=400, msg="图片处理失败，请换一张图片重试"), 400
        if saved_ext != real_ext:
            # 重新编码后格式可能与嗅探结果不同（例如 jpg 被识别为 jpeg），以实际保存为准
            new_dest = os.path.join(target_dir, f"{os.path.splitext(filename)[0]}.{saved_ext}")
            os.replace(dest, new_dest)
            filename = os.path.basename(new_dest)
            dest = new_dest

    rel_path = f"/static/uploads/{user.id}/{os.path.basename(target_dir)}/{filename}"
    return jsonify(code=0, msg="上传成功", data={"url": rel_path, "size": os.path.getsize(dest)})
