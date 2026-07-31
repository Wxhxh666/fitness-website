from flask import jsonify, request
from . import contact_bp
from models.contact import ContactMessage
from models import db


VALID_SUBJECTS = {"course", "plan", "coach", "partner", "other"}


@contact_bp.route("", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    errors = []
    if not name:
        errors.append("请输入姓名")
    if not email or "@" not in email:
        errors.append("请输入有效邮箱")
    if not subject or subject not in VALID_SUBJECTS:
        errors.append("请选择有效主题")
    if not message:
        errors.append("请输入留言内容")

    if errors:
        return jsonify(code=400, msg="; ".join(errors)), 400

    record = ContactMessage(
        name=name, email=email, phone=phone,
        subject=subject, message=message
    )
    db.session.add(record)
    db.session.commit()

    return jsonify(code=0, msg="success", data={
        "id": record.id,
        "created_at": record.created_at.isoformat() if hasattr(record.created_at, "isoformat") else str(record.created_at),
    })
