"""
JWT 令牌工具 + 认证中间件

约定：
- 令牌只携带 user_id，权限一律以数据库中的 User 为准（不在 token 里放 is_admin，
  否则管理员被降权后旧 token 仍是管理员）。
- 所有时间使用带时区的 UTC，避免 naive datetime 与本地时间混用。
"""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, jsonify, request

from models import db
from models.auth import User

JWT_ALGORITHM = "HS256"


def _now():
    return datetime.now(timezone.utc)


def generate_token(user_id: int) -> str:
    """生成 JWT 令牌"""
    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        # 正常不会走到这里（启动时已校验），兜底避免用空密钥签名
        raise RuntimeError("JWT_SECRET 未配置")
    days = int(current_app.config.get("JWT_EXPIRATION_DAYS", 7))
    now = _now()
    payload = {
        "sub": str(user_id),
        "user_id": user_id,          # 兼容旧前端 / 旧 token
        "iat": now,
        "exp": now + timedelta(days=days),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """验证令牌，返回 payload 或 None"""
    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        return None
    try:
        return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """从 Authorization header 获取当前用户；未登录 / 令牌失效 / 账号被禁用返回 None"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    payload = verify_token(auth[7:])
    if payload is None:
        return None
    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        return None
    user = db.session.get(User, user_id)
    if user is None or user.is_active is False:
        return None
    return user


def _unauthorized(msg="请先登录"):
    resp = jsonify(code=401, msg=msg)
    resp.status_code = 401
    resp.headers["WWW-Authenticate"] = "Bearer"
    return resp


def require_auth(f):
    """要求登录的装饰器：视图函数通过 user 关键字参数拿到当前用户"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return _unauthorized()
        return f(*args, user=user, **kwargs)
    return decorated


def require_admin(f):
    """要求管理员权限"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return _unauthorized()
        if not user.is_admin:
            return jsonify(code=403, msg="无管理员权限"), 403
        return f(*args, user=user, **kwargs)
    return decorated


def require_coach(f):
    """要求认证教练权限（管理员视作教练，便于后台排查问题）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return _unauthorized()
        if not (user.is_coach or user.is_admin):
            return jsonify(code=403, msg="仅认证教练可访问，请先在个人中心完成教练认证"), 403
        return f(*args, user=user, **kwargs)
    return decorated
