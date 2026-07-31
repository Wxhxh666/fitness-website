import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from utils.auth import require_auth

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi", "mkv"}
MAX_SIZE = 2 * 1024 * 1024  # 2MB
VIDEO_MAX_SIZE = 200 * 1024 * 1024  # 200MB

def allowed_file(filename, allow_video=False):
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    if allow_video:
        return ext in ALLOWED_EXTENSIONS or ext in VIDEO_EXTENSIONS
    return ext in ALLOWED_EXTENSIONS

@upload_bp.route("/upload", methods=["POST"])
@require_auth
def upload_file(user):
    if "file" not in request.files:
        return jsonify(code=400, msg="未选择文件"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(code=400, msg="文件名为空"), 400
    
    # Determine if video upload (from request param or extension)
    allow_video = request.form.get("type") == "video"
    
    # Check file size
    file.seek(0, 2)  # seek to end
    size = file.tell()
    file.seek(0)  # seek back to start
    
    max_size = VIDEO_MAX_SIZE if allow_video else MAX_SIZE
    size_label = "200MB" if allow_video else "2MB"
    if size > max_size:
        return jsonify(code=400, msg=f"文件大小不能超过 {size_label}"), 400
    
    if not allowed_file(file.filename, allow_video):
        allowed_list = "png/jpg/jpeg/gif/webp" if not allow_video else "png/jpg/jpeg/gif/webp/mp4/webm/mov/avi/mkv"
        return jsonify(code=400, msg=f"仅支持 {allowed_list} 格式"), 400
    
    # Save with UUID name
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    url = f"/static/uploads/{filename}"
    
    return jsonify(code=0, msg="上传成功", data={"url": url})

