import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "development-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'warrigal_park.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_ENABLED = os.environ.get("ADMIN_ENABLED", "false").lower() in {"1", "true", "yes"}
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "WarrigalPark2026!")
    SESSION_COOKIE_HTTPONLY = True
