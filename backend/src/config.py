import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Settings:
    port: int
    flask_env: str
    database_url: str
    secret_key: str
    jwt_secret: str
    frontend_url: str
    backend_url: str
    cors_origins: List[str]
    upload_folder: str
    max_file_size_bytes: int
    allowed_extensions: List[str]


def load_settings() -> Settings:
    cors_raw = os.environ.get("CORS_ORIGINS", "*")
    cors_list = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

    return Settings(
        port=int(os.environ.get("PORT", 10000)),
        flask_env=os.environ.get("FLASK_ENV", "production"),
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./local.db"),
        secret_key=os.environ.get("SECRET_KEY", "change-me"),
        jwt_secret=os.environ.get("JWT_SECRET", "change-me-jwt"),
        frontend_url=os.environ.get("FRONTEND_URL", "http://localhost:5173"),
        backend_url=os.environ.get("BACKEND_URL", "http://localhost:10000"),
        cors_origins=cors_list or ["*"],
        upload_folder=os.environ.get("UPLOAD_FOLDER", "/tmp/uploads"),
        max_file_size_bytes=10 * 1024 * 1024,
        allowed_extensions=["pdf", "png", "jpg", "jpeg", "gif", "doc", "docx"],
    )
