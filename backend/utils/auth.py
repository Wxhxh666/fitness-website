"""
JWT 令牌工具 + 认证中间件
"""
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import jwt

from models import db
from models.auth import User

JWT_ALGORITHM = "HS256"


def generate_token(user_id: int) -> str:
    """生成 JWT 令牌（7天有效）"""
    secret = current_app.config.get("JWT_SECRET", "fitluxe-jwt-secret")
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """验证令牌，返回 payload 或 None"""
    secret = current_app.config.get("JWT_SECRET", "fitluxe-jwt-secret")
    try:
        return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """从 Authorization header 获取当前用户"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]  # 去掉 "Bearer "
    payload = verify_token(token)
    if payload is None:
        return None
    return User.query.get(payload.get("user_id"))


def require_auth(f):
    """要求登录的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify(code=401, msg="请先登录"), 401
        return f(user=user, *args, **kwargs)
    return decorated

def require_admin(f):
    """要求管理员权限"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify(code=401, msg="请先登录"), 401
        if not user.is_admin:
            return jsonify(code=403, msg="无管理员权限"), 403
        return f(user=user, *args, **kwargs)
    return decorated
