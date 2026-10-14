import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "fitluxe-secret-key-2026")

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
    JWT_SECRET = os.environ.get("JWT_SECRET", "fitluxe-jwt-secret-2026")
    JWT_EXPIRATION_DAYS = 7

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
