"""
QuizMind AI - Configuration
Reads all sensitive/environment-specific values from environment variables
(loaded from a local .env file). Nothing secret is hardcoded here.
"""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _database_uri():
    """Build the SQLAlchemy database URI, defaulting to local SQLite."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return "sqlite:///" + os.path.join(BASE_DIR, "quizmind.db")
    # Normalize old-style mysql:// to the pymysql driver
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    return url


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-dev-key-please-change")

    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "syllabus")
    ALLOWED_SYLLABUS_EXTENSIONS = {"pdf", "txt"}
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 10)) * 1024 * 1024

    # AI provider
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "demo").lower()
    AI_API_KEY = os.environ.get("AI_API_KEY", "")
    AI_MODEL = os.environ.get("AI_MODEL", "gemini-1.5-flash")

    # Quiz
    DEFAULT_QUIZ_TIME_MINUTES = int(os.environ.get("DEFAULT_QUIZ_TIME_MINUTES", 30))

    # Sessions
    REMEMBER_COOKIE_DURATION_DAYS = 14
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
