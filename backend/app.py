import logging
import os
import secrets
import time
import uuid

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from config import get_config
from models import db


def assert_secure_config(app):
    """
    启动前的安全自检：
    - 生产环境缺少 SECRET_KEY / JWT_SECRET 直接拒绝启动（fail fast）；
    - 开发环境自动生成临时密钥并打印醒目警告，重启后旧 token 失效。
    """
    missing = [k for k in ("SECRET_KEY", "JWT_SECRET") if len(app.config.get(k) or "") < 32]
    if not missing:
        return
    if not app.config.get("IS_DEV"):
        raise RuntimeError(
            "缺少安全密钥：" + ", ".join(missing) +
            "。请在 backend/.env 中配置（python -c \"import secrets; print(secrets.token_hex(32))\"），"
            "或设置 APP_ENV=development 以本地开发模式启动。"
        )
    for key in missing:
        app.config[key] = secrets.token_hex(32)
    app.logger.warning(
        "[安全警告] 开发模式下自动生成了临时 %s，重启后已签发的 token 会失效；"
        "正式部署请在 .env 中显式配置。", ", ".join(missing),
    )


def register_error_handlers(app):
    """统一错误出口，保证任何异常都返回 {code, msg} 而不是 HTML 错误页"""

    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        if e.code == 404:
            msg = "接口不存在"
        elif e.code == 405:
            msg = "请求方法不被允许"
        elif e.code == 413:
            msg = "上传内容过大"
        else:
            msg = e.description or "请求失败"
        return jsonify(code=e.code, msg=msg), e.code

    @app.errorhandler(Exception)
    def handle_uncaught(e: Exception):
        # 关键：回滚会话，避免脏事务串到下一个请求，表现为“偶发的莫名报错”
        try:
            db.session.rollback()
        except Exception:  # noqa: BLE001 - 回滚失败不应掩盖原始异常
            pass
        app.logger.exception("[unhandled] %s %s", request.method, request.path)
        if app.config.get("DEBUG"):
            # 开发环境把异常信息带出去，方便定位；生产环境绝不暴露内部细节
            return jsonify(code=500, msg=f"服务器内部错误：{e}"), 500
        return jsonify(code=500, msg="服务器内部错误，请稍后重试"), 500


def register_request_logging(app):
    """请求耗时日志：只为慢请求和错误请求打日志，避免刷屏"""

    @app.before_request
    def _start_timer():
        g.request_id = uuid.uuid4().hex[:12]
        g.request_started = time.perf_counter()

    @app.after_request
    def _log_request(resp):
        started = getattr(g, "request_started", None)
        if started is None:
            return resp
        cost_ms = (time.perf_counter() - started) * 1000
        resp.headers["X-Request-Id"] = getattr(g, "request_id", "-")
        if cost_ms > 1000 or resp.status_code >= 500:
            app.logger.warning(
                "[slow] %s %s -> %s %.0fms rid=%s",
                request.method, request.path, resp.status_code, cost_ms,
                getattr(g, "request_id", "-"),
            )
        return resp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    # 全局上限需 >= 上传接口允许的最大值（config: 图片 2MB / 视频 200MB），
    # 具体类型限制由 upload.py 内校验；额外留 2MB 给 multipart 头部与表单字段
    app.config["MAX_CONTENT_LENGTH"] = app.config["UPLOAD_VIDEO_MAX_BYTES"] + 2 * 1024 * 1024

    assert_secure_config(app)

    if not app.config.get("DEBUG") and app.config.get("ENV_NAME") != "testing":
        # 生产环境日志级别与格式
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )

    # CORS
    origins = app.config.get("CORS_ORIGINS", "")
    CORS(
        app,
        resources={r"/api/*": {
            "origins": [o.strip() for o in origins.split(",") if o.strip()],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["X-Request-Id", "Content-Disposition"],
            "supports_credentials": True,
        }},
    )

    # DB
    db.init_app(app)

    register_error_handlers(app)
    register_request_logging(app)

    # Register blueprints
    from routes.exercises import exercises_bp
    from routes.plans import plans_bp
    from routes.body_metrics import body_metrics_bp
    from routes.contact import contact_bp
    from routes.site import site_bp
    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.admin import admin_bp
    from routes.user_plans import user_plans_bp
    from routes.ai import ai_bp
    from routes.workouts import workouts_bp
    from routes.achievements import achievements_bp

    app.register_blueprint(exercises_bp, url_prefix="/api/exercises")
    app.register_blueprint(plans_bp, url_prefix="/api/plans")
    app.register_blueprint(body_metrics_bp, url_prefix="/api/body-metrics")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(site_bp, url_prefix="/api/site")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(user_plans_bp, url_prefix="/api/user-plans")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(workouts_bp, url_prefix="/api/workouts")
    app.register_blueprint(achievements_bp, url_prefix="/api/achievements")

    # Root - API index
    @app.route("/api", methods=["GET"])
    def api_index():
        return jsonify(code=0, msg="FITLUXE API v1.0", data={
            "docs": "/api/docs",
            "health": "/api/health",
            "endpoints": [
                "GET  /api/exercises/categories",
                "GET  /api/exercises[?category=&difficulty=&keyword=]",
                "GET  /api/exercises/:id",
                "GET  /api/plans/goals",
                "GET  /api/plans[?goal=&difficulty=]",
                "GET  /api/plans/:id",
                "POST /api/body-metrics/bmi",
                "POST /api/body-metrics/calculate",
                "GET|POST /api/body-metrics/records        [需登录]",
                "GET  /api/body-metrics/records/compare    [需登录]",
                "DELETE /api/body-metrics/records/:id      [需登录]",
                "GET  /api/body-metrics/export             [需登录]",
                "GET|POST /api/body-metrics/profile        [需登录]",
                "GET|POST /api/body-metrics/goals          [需登录]",
                "POST /api/ai/diet-plan                    [需登录]",
                "GET|POST /api/ai/diet-plans               [需登录]",
                "GET|POST /api/ai/diet-logs                [需登录]",
                "POST /api/ai/weekly-review                [需登录]",
                "GET|POST /api/workouts                    [需登录]",
                "GET  /api/workouts/:id                    [需登录]",
                "POST /api/workouts/:id/sets               [需登录]",
                "GET  /api/workouts/overview               [需登录]",
                "GET  /api/workouts/prs                    [需登录]",
                "GET  /api/workouts/calendar?month=        [需登录]",
                "GET  /api/achievements                    [需登录]",
                "POST /api/contact",
                "GET  /api/site/contact-info",
            ],
        })

    # Health check：liveness + readiness（数据库可用性）
    @app.route("/api/health", methods=["GET"])
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            db_ok = True
        except Exception as exc:  # noqa: BLE001 - 健康检查需要吞掉具体异常类型
            app.logger.warning("[health] 数据库不可用: %s", exc)
            db_ok = False
        payload = {
            "db": "ok" if db_ok else "down",
            "env": app.config.get("ENV_NAME"),
            "ai_configured": bool(app.config.get("DEEPSEEK_API_KEY")) or bool(app.config.get("DOUBAO_API_KEY")),
        }
        if not db_ok:
            return jsonify(code=503, msg="unhealthy", data=payload), 503
        return jsonify(code=0, msg="healthy", data=payload)

    # Root redirect
    @app.route("/", methods=["GET"])
    def root():
        return jsonify(
            code=0,
            msg="FITLUXE API",
            data={
                "api": "/api",
                "docs": "See api.md in the project root for full documentation.",
            },
        )

    return app


app = create_app()

if __name__ == "__main__":
    # 生产环境请用 gunicorn / waitress 启动，这里的 run 只用于本地开发
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        debug=app.config.get("DEBUG", False),
    )
