"""
轻量限流（进程内固定窗口）

适用场景：单进程开发 / 小规模部署。多实例部署时各进程独立计数，
应按需替换为 Redis 或 Flask-Limiter。

用法：
    @auth_bp.route("/send-code", methods=["POST"])
    @rate_limit(limit=5, window=60, scope="send_code")
    def send_code(): ...
"""
import threading
import time
from functools import wraps

from flask import current_app, jsonify, request


class MemoryRateLimiter:
    """线程安全的固定窗口计数器"""

    def __init__(self):
        self._buckets: dict[str, tuple[float, int]] = {}
        self._lock = threading.Lock()
        self._last_gc = time.time()

    def hit(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """返回 (是否放行, 需等待秒数)"""
        now = time.time()
        with self._lock:
            self._gc_if_needed(now)
            window_start, count = self._buckets.get(key, (now, 0))
            if now - window_start >= window:
                window_start, count = now, 0
            count += 1
            self._buckets[key] = (window_start, count)
            if count > limit:
                retry_after = max(1, int(window - (now - window_start)))
                return False, retry_after
            return True, 0

    def reset(self, prefix: str | None = None):
        with self._lock:
            if prefix is None:
                self._buckets.clear()
            else:
                for k in [k for k in self._buckets if k.startswith(prefix)]:
                    self._buckets.pop(k, None)

    def _gc_if_needed(self, now: float):
        """entry 数量超过阈值时清理过期窗口，避免长期运行内存增长"""
        if len(self._buckets) < 1000 or now - self._last_gc < 60:
            return
        expired = [k for k, (start, _) in self._buckets.items() if now - start > 3600]
        for k in expired:
            self._buckets.pop(k, None)
        self._last_gc = now


limiter = MemoryRateLimiter()


def client_ip() -> str:
    """取客户端 IP：优先 X-Forwarded-For 首个地址（部署在反向代理后），否则 remote_addr"""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def json_field(field: str):
    """从 JSON body 中取字段作为限流维度（如手机号 / 邮箱）"""
    def _getter() -> str:
        data = request.get_json(silent=True) or {}
        return str(data.get(field) or "").strip().lower()
    return _getter


def rate_limit(limit: int, window: int, scope: str, key_func=None):
    """
    :param limit:  窗口内允许的次数
    :param window: 窗口长度（秒）
    :param scope:  限流维度前缀，便于 reset / 排查
    :param key_func: 自定义限流键（默认按客户端 IP）
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_app.config.get("RATE_LIMIT_ENABLED", True):
                return fn(*args, **kwargs)
            subject = key_func() if key_func else client_ip()
            if subject:
                allowed, retry_after = limiter.hit(f"{scope}:{subject}", limit, window)
                if not allowed:
                    return too_many_response(retry_after)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def too_many_response(retry_after: int):
    resp = jsonify(code=429, msg=f"操作过于频繁，请 {retry_after} 秒后再试")
    resp.status_code = 429
    resp.headers["Retry-After"] = str(retry_after)
    return resp


def check_budget(key: str, limit: int, window: int):
    """
    在视图内部按业务维度限流（例如按用户 id 限制 AI 调用次数）。
    返回 None 表示放行，否则返回可直接 return 的 429 响应。
    """
    if not current_app.config.get("RATE_LIMIT_ENABLED", True):
        return None
    allowed, retry_after = limiter.hit(key, limit, window)
    if not allowed:
        return too_many_response(retry_after)
    return None
