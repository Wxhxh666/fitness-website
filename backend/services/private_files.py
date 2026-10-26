# -*- coding: utf-8 -*-
"""
证件类敏感文件存储

与公开上传（/static/uploads，静态目录直接可访问）不同，身份证、资质凭证属于
高敏 PII：存放在 backend/storage/private/ 下，Flask 不对此目录做静态服务，
读取必须经 routes/coaches.py 的受保护接口做归属校验（本人或管理员）。

存储相对路径形如 credentials/<user_id>/<uuid>.<ext>，落库的也只是这个
相对路径，URL 不可猜测即可访问的问题不存在——没有接口谁也读不到。
"""
import os
import uuid

from werkzeug.utils import secure_filename  # noqa: F401  仅用于文件名长度防御

PRIVATE_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "storage", "private",
))

# 目前只有证件类，后续私密文件扩展类别只需在 ALLOWED_KINDS 加键
ALLOWED_KINDS = {"credentials"}

MAX_IMAGE_EDGE = 4096
PIL_FORMAT = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def private_abs_path(rel_path: str) -> str | None:
    """把相对路径解析为绝对路径；防御路径穿越，越界返回 None"""
    if not rel_path:
        return None
    rel_norm = os.path.normpath(rel_path).replace("\\", "/").lstrip("/")
    kind = rel_norm.split("/", 1)[0]
    if kind not in ALLOWED_KINDS:
        return None
    abs_path = os.path.normpath(os.path.join(PRIVATE_ROOT, rel_norm))
    if not abs_path.startswith(PRIVATE_ROOT + os.sep):
        return None
    return abs_path


def save_credential_image(user_id: int, file_storage) -> tuple[str | None, str]:
    """
    保存一张证件/凭证图片到私有目录。复用公开上传同级别的防护：
    magic bytes 嗅探 + Pillow 解码重编码（剥 EXIF，含 GPS）+ 像素上限。
    返回 (相对路径, 错误信息)；成功时错误信息为空。
    """
    if file_storage is None or not file_storage.filename:
        return None, "未选择文件"

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size == 0:
        return None, "文件为空"
    if size > 8 * 1024 * 1024:
        return None, "证件图片大小不能超过 8MB"

    head = file_storage.stream.read(32)
    file_storage.stream.seek(0)
    if head.startswith(b"\xff\xd8\xff"):
        sniffed = "jpg"
    elif head.startswith(b"\x89PNG\r\n\x1a\n"):
        sniffed = "png"
    elif len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        sniffed = "webp"
    else:
        return None, "证件必须是 jpg/png/webp 图片"

    target_dir = os.path.join(PRIVATE_ROOT, "credentials", str(user_id))
    os.makedirs(target_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    dest = os.path.join(target_dir, filename)

    if not PIL_AVAILABLE:
        # 与公开上传同策略：没 Pillow 时退化为原样落盘（生产环境必须安装）
        ext = {"jpg": ".jpg", "png": ".png", "webp": ".webp"}[sniffed]
        filename = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(target_dir, filename)
        file_storage.stream.seek(0)
        file_storage.save(dest)
        return f"credentials/{user_id}/{filename}", ""

    try:
        img = Image.open(file_storage.stream)
        img.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return None, "图片文件损坏或不是受支持的图片格式"

    fmt = (img.format or "").upper()
    if fmt not in PIL_FORMAT:
        return None, "证件必须是 jpg/png/webp 图片"

    try:
        img = ImageOps.exif_transpose(img)
    except Exception:  # noqa: BLE001
        pass
    if max(img.size) > MAX_IMAGE_EDGE:
        img.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.LANCZOS)
    # 统一转 JPEG：证件类不需要透明通道，压缩率更好，且不带 exif 参数即剥离 EXIF
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(dest, format="JPEG", quality=88, optimize=True)

    return f"credentials/{user_id}/{filename}", ""
