import random
import string
from datetime import datetime, timedelta
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from utils.auth import generate_token, get_current_user
from models.auth import User, VerificationCode
from models.profile_request import ProfileChangeRequest
from models.body_record import BodyRecord, BodyProfile
from models.diet_log import DietLog
from models.diet_plan import DietPlan
from models.user_plan import UserPlan

from . import auth_bp


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
    """注册（账号 + 密码，无需验证码）

    说明：应产品要求移除了验证码校验。代价是无法验证邮箱/手机号归属，
    因此这里补上格式校验与重复注册检查作为基本防线。
    """
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip()
    password = (data.get("password") or "").strip()

    if not identifier:
        return jsonify(code=400, msg="请输入手机号或邮箱"), 400
    if not password or len(password) < 6:
        return jsonify(code=400, msg="密码至少6位"), 400

    # 格式校验：含 @ 视为邮箱，否则视为手机号。
    # 用“含 @”而不是“@ 和 . 都有”来判类型，否则 "abc@" 这类会落进手机号分支，
    # 报出“手机号格式不正确”这种误导性提示。
    if "@" in identifier:
        if not is_valid_email(identifier):
            return jsonify(code=400, msg="邮箱格式不正确"), 400
    else:
        if not is_valid_phone(identifier):
            return jsonify(code=400, msg="手机号格式不正确（需11位数字）"), 400

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


@auth_bp.route("/bind-phone", methods=["POST"])
def bind_phone():
    """绑定 / 更换手机号"""
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()
    if not is_valid_phone(phone):
        return jsonify(code=400, msg="手机号格式不正确（需11位数字）"), 400
    existing = User.query.filter_by(phone=phone).first()
    if existing and existing.id != user.id:
        return jsonify(code=400, msg="该手机号已被其他账号绑定"), 400
    user.phone = phone
    db.session.commit()
    return jsonify(code=0, msg="手机号绑定成功", data={"phone": user.phone})


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    """修改登录密码（校验原密码）"""
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password") or ""
    new_password = (data.get("new_password") or "").strip()
    if len(new_password) < 6:
        return jsonify(code=400, msg="新密码至少6位"), 400
    if user.password_hash and not check_password_hash(user.password_hash, old_password):
        return jsonify(code=400, msg="原密码不正确"), 400
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify(code=0, msg="密码修改成功")


@auth_bp.route("/preferences", methods=["GET"])
def get_preferences():
    """读取系统偏好（AI模型 / 度量单位 / 通知开关）"""
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    return jsonify(code=0, msg="success", data={
        "ai_model": user.ai_model or "deepseek-flash",
        "unit_system": user.unit_system or "metric",
        "notification_enabled": bool(user.notification_enabled),
    })


@auth_bp.route("/preferences", methods=["PUT"])
def update_preferences():
    """保存系统偏好到用户表（同步身材档案的单位）"""
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    data = request.get_json(silent=True) or {}
    if "ai_model" in data:
        model = data["ai_model"]
        if model not in ("deepseek-flash", "doubao-lite"):
            return jsonify(code=400, msg="不支持的AI模型"), 400
        user.ai_model = model
    if "unit_system" in data:
        unit = data["unit_system"]
        if unit not in ("metric", "imperial"):
            return jsonify(code=400, msg="不支持的度量单位"), 400
        user.unit_system = unit
        # 同步到身材档案，保持 BodyData 页面单位一致
        bp = BodyProfile.query.filter_by(user_id=user.id).first()
        if bp:
            bp.unit_system = unit
    if "notification_enabled" in data:
        user.notification_enabled = bool(data["notification_enabled"])
    db.session.commit()
    return jsonify(code=0, msg="偏好已保存", data={
        "ai_model": user.ai_model,
        "unit_system": user.unit_system,
        "notification_enabled": bool(user.notification_enabled),
    })


@auth_bp.route("/dashboard-stats", methods=["GET"])
def dashboard_stats():
    """个人中心仪表盘：统计数字 + 近30天体重序列 + 最新身材记录"""
    user = get_current_user()
    if not user:
        return jsonify(code=401, msg="未登录"), 401
    uid = user.id
    measurement_count = BodyRecord.query.filter_by(user_id=uid).count()
    diet_plan_count = DietPlan.query.filter_by(user_id=uid).count()
    plan_count = UserPlan.query.filter_by(user_id=uid).count()
    checkin_days = db.session.query(DietLog.log_date).filter_by(user_id=uid).distinct().count()

    since = (datetime.utcnow() - timedelta(days=29)).strftime("%Y-%m-%d")
    weights = BodyRecord.query.filter(
        BodyRecord.user_id == uid,
        BodyRecord.record_date >= since,
        BodyRecord.weight_kg.isnot(None),
    ).order_by(BodyRecord.record_date.asc(), BodyRecord.id.asc()).all()
    weight_series = [{"date": r.record_date, "weight_kg": r.weight_kg} for r in weights]

    latest = BodyRecord.query.filter_by(user_id=uid).order_by(
        BodyRecord.record_date.desc(), BodyRecord.id.desc()
    ).first()
    return jsonify(code=0, msg="success", data={
        "stats": {
            "measurements": measurement_count,
            "diet_plans": diet_plan_count,
            "plans": plan_count,
            "checkin_days": checkin_days,
        },
        "weight_series": weight_series,
        "latest_record": latest.to_dict() if latest else None,
    })

