import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    APP_ENV = os.environ.get("APP_ENV", "development").lower()

    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if APP_ENV == "production":
            raise RuntimeError("SECRET_KEY must be configured in production.")
        SECRET_KEY = "dev-only-change-me"

    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = (
        database_url
        or "sqlite:///" + os.path.join(BASE_DIR, "database", "bluelens.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    EXPORT_FOLDER = os.environ.get("EXPORT_FOLDER", os.path.join(BASE_DIR, "exports"))
    REPORT_FOLDER = os.environ.get("REPORT_FOLDER", os.path.join(BASE_DIR, "reports"))
    LOG_FOLDER = os.environ.get("LOG_FOLDER", os.path.join(BASE_DIR, "logs"))

    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"txt", "log", "csv", "xlsx", "pdf", "docx"}

    SEED_DEMO_USERS = _as_bool(
        os.environ.get("SEED_DEMO_USERS"),
        default=APP_ENV != "production",
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool(
        os.environ.get("SESSION_COOKIE_SECURE"),
        default=APP_ENV == "production",
    )
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
