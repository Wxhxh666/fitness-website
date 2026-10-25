import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _env_bool(key, default=False):
    return os.environ.get(key, "1" if default else "0").strip().lower() in ("1", "true", "yes", "on")


# 默认按生产对待：没有显式声明开发环境时，缺失密钥必须启动失败，
# 避免"忘记配密钥就直接上线"这种最常见的事故。
APP_ENV = os.environ.get("APP_ENV", "production").strip().lower()
IS_DEV = APP_ENV in ("dev", "development", "local", "test", "testing")


class Config:
    """Base configuration."""

    ENV_NAME = APP_ENV
    IS_DEV = IS_DEV
    DEBUG = IS_DEV and _env_bool("FLASK_DEBUG", True)

    # 安全密钥：只从环境变量读取，代码里不留任何可用的默认值。
    # 开发环境允许留空（启动时自动生成临时密钥，见 app.assert_secure_config），
    # 生产环境留空则拒绝启动。
    SECRET_KEY = os.environ.get("SECRET_KEY") or ""
    JWT_SECRET = os.environ.get("JWT_SECRET") or ""

    # MySQL
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "fitluxe")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # 取连接前探活，避免 MySQL 断连后报 "server has gone away"
        "pool_recycle": 3600,
    }

    # CORS
    # 注意：localhost 与 127.0.0.1 在浏览器看来是“不同的源”，必须都放行，
    # 否则从 127.0.0.1:4173 打开的页面会因为缺少 CORS 响应头而拿不到任何数据
    # （接口本身返回 200，但响应会被浏览器丢弃，表现为“页面数据加载不出来”）。
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:4173,"
        "http://127.0.0.1:3000,http://127.0.0.1:4173",
    )

    # JSON
    JSON_AS_ASCII = False
    RESTFUL_JSON = {"ensure_ascii": False}

    # JWT
    JWT_EXPIRATION_DAYS = int(os.environ.get("JWT_EXPIRATION_DAYS", "7"))

    # 上传限制
    UPLOAD_IMAGE_MAX_BYTES = int(os.environ.get("UPLOAD_IMAGE_MAX_BYTES", str(2 * 1024 * 1024)))
    UPLOAD_VIDEO_MAX_BYTES = int(os.environ.get("UPLOAD_VIDEO_MAX_BYTES", str(200 * 1024 * 1024)))
    UPLOAD_DAILY_QUOTA = int(os.environ.get("UPLOAD_DAILY_QUOTA", "50"))  # 每个用户每天最多上传次数

    # 限流（单进程内存实现；多实例部署请换成 Redis / Flask-Limiter）
    RATE_LIMIT_ENABLED = _env_bool("RATE_LIMIT_ENABLED", True)

    # DeepSeek AI 饮食方案
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    DEEPSEEK_MOCK = os.environ.get("DEEPSEEK_MOCK", "0") == "1"
    DEEPSEEK_TIMEOUT = 120

    # Doubao (火山方舟) AI 支持（可选，配置了 key 才启用 doubao-lite）
    DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
    DOUBAO_BASE_URL = os.environ.get("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    DOUBAO_MODEL = os.environ.get("DOUBAO_MODEL", "doubao-lite")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    RATE_LIMIT_ENABLED = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "local": DevelopmentConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def get_config():
    return CONFIG_MAP.get(APP_ENV, ProductionConfig)
