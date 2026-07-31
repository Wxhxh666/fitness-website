import random
import string
from datetime import datetime, timedelta
from flask import jsonify, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from utils.auth import generate_token, get_current_user
from models.auth import User, VerificationCode
from models.profile_request import ProfileChangeRequest

auth_bp = Blueprint("auth", __name__)


def generate_code(length=6):
    return "".join(random.choices(string.digits, k=length))


def is_valid_phone(phone: str) -> bool:
    return len(phone) == 11 and phone.isdigit()


def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email


@auth_bp.route("/send-code", methods=["POST"])
def send_code():
    """发送验证码"""
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip()
    purpose = data.get("purpose", "login")

    if not identifier:
        return jsonify(code=400, msg="请输入手机号或邮箱"), 400

    if "@" in identifier:
        if not is_valid_email(identifier):
            return jsonify(code=400, msg="邮箱格式不正确"), 400
    else:
        if not is_valid_phone(identifier):
            return jsonify(code=400, msg="手机号格式不正确（需11位数字）"), 400

    # 生成验证码
    code = generate_code()

    # 清理同一账号的过期验证码
    VerificationCode.query.filter(
        VerificationCode.identifier == identifier,
        VerificationCode.is_used == False,
        VerificationCode.expires_at < datetime.utcnow()
    ).delete()

    # 存储验证码（5分钟有效）
    vc = VerificationCode(
        identifier=identifier,
        code=code,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.session.add(vc)
    db.session.commit()

    # 开发环境直接返回验证码，方便测试
    print(f"\n[验证码] {identifier} -> {code} (有效期5分钟)\n")

    return jsonify(code=0, msg="验证码已发送", data={
        "debug_code": code,  # 开发调试用，生产环境应移除
        "expires_in": 300,
    })


@auth_bp.route("/register", methods=["POST"])
def register():
    """注册"""
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip()
    code = (data.get("code") or "").strip()
    password = (data.get("password") or "").strip()

    if not identifier:
        return jsonify(code=400, msg="请输入手机号或邮箱"), 400
    if not code:
        return jsonify(code=400, msg="请输入验证码"), 400
    if not password or len(password) < 6:
        return jsonify(code=400, msg="密码至少6位"), 400

    # 校验验证码
    vc = VerificationCode.query.filter_by(
        identifier=identifier, code=code, is_used=False
    ).order_by(VerificationCode.id.desc()).first()

    if not vc or vc.is_expired():
        return jsonify(code=400, msg="验证码无效或已过期"), 400

    # 检查是否已注册
    if "@" in identifier:
        existing = User.query.filter_by(email=identifier).first()
    else:
        existing = User.query.filter_by(phone=identifier).first()

    if existing:
        return jsonify(code=400, msg="该账号已注册，请直接登录"), 400

    # 创建用户
    user = User(
        email=identifier if "@" in identifier else None,
        phone=identifier if "@" not in identifier else None,
        password_hash=generate_password_hash(password),
        nickname=identifier[:4] + "***",
    )
    db.session.add(user)

    # 标记验证码已使用
    vc.is_used = True
    db.session.commit()
    token = generate_token(user.id)

    return jsonify(code=0, msg="注册成功", data={"user_id": user.id, "nickname": user.nickname, "token": token, "is_admin": user.is_admin, "avatar_url": user.avatar_url})


@auth_bp.route("/login", methods=["POST"])
def login():
    """验证码登录"""
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip()
    code = (data.get("code") or "").strip()

    if not identifier:
        return jsonify(code=400, msg="请输入手机号或邮箱"), 400
    if not code:
        return jsonify(code=400, msg="请输入验证码"), 400

    # 校验验证码
    vc = VerificationCode.query.filter_by(
        identifier=identifier, code=code, is_used=False
    ).order_by(VerificationCode.id.desc()).first()

    if not vc or vc.is_expired():
        return jsonify(code=400, msg="验证码无效或已过期"), 400

    # 查找用户（未注册则提示）
    if "@" in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        user = User.query.filter_by(phone=identifier).first()

    if not user:
        return jsonify(code=400, msg="该用户不存在，请先注册"), 400
    if user.is_active is False:
        return jsonify(code=400, msg="您的账号因异常被禁用，请联系管理员"), 400

    user.last_login_at = datetime.utcnow()
    vc.is_used = True
    db.session.commit()
    token = generate_token(user.id)

    return jsonify(code=0, msg="登录成功", data={"user_id": user.id, "nickname": user.nickname or identifier[:4] + "***", "token": token, "is_admin": user.is_admin, "avatar_url": user.avatar_url})


@auth_bp.route("/password-login", methods=["POST"])
def password_login():
    """密码登录"""
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip()
    password = (data.get("password") or "").strip()

    if not identifier or not password:
        return jsonify(code=400, msg="请输入账号和密码"), 400

    if "@" in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        user = User.query.filter_by(phone=identifier).first()

    if not user or not user.password_hash:
        return jsonify(code=400, msg="账号或密码错误"), 400
    if user.is_active is False:
        return jsonify(code=400, msg="您的账号因异常被禁用，请联系管理员"), 400

    if not check_password_hash(user.password_hash, password):
        return jsonify(code=400, msg="账号或密码错误"), 400

    user.last_login_at = datetime.utcnow()
    db.session.commit()
    token = generate_token(user.id)

    return jsonify(code=0, msg="登录成功", data={"user_id": user.id, "nickname": user.nickname or identifier[:4] + "***", "token": token, "is_admin": user.is_admin, "avatar_url": user.avatar_url})




@auth_bp.route("/me", methods=["GET"])
def get_current_user_info():
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    return jsonify(code=0, msg="success", data=user.to_dict())
@auth_bp.route("/profile", methods=["GET"])
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    pending = ProfileChangeRequest.query.filter_by(user_id=user.id, status="pending").all()
    data = user.to_dict()
    pending_info = {}
    for p in pending:
        pending_info[p.field_name] = {"new_value": p.new_value, "status": "pending"}
    data["pending_changes"] = pending_info
    return jsonify(code=0, msg="success", data=data)

@auth_bp.route("/profile", methods=["POST"])
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    data = request.get_json(silent=True) or {}
    field = data.get("field")
    value = (data.get("value") or "").strip()
    if field not in ("nickname", "avatar"):
        return jsonify(code=400, msg="仅支持修改 nickname 或 avatar"), 400
    if not value:
        return jsonify(code=400, msg="值不能为空"), 400
    model_field = {"avatar": "avatar_url"}.get(field, field)
    old_value = getattr(user, model_field, "") or ""
    existing = ProfileChangeRequest.query.filter_by(
        user_id=user.id, field_name=field, status="pending"
    ).first()
    if existing:
        return jsonify(code=400, msg="该字段已有待审核申请"), 400
    req = ProfileChangeRequest(
        user_id=user.id, field_name=field,
        old_value=old_value, new_value=value
    )
    db.session.add(req)
    db.session.commit()
    return jsonify(code=0, msg="申请已提交，等待审核", data={"id": req.id})

