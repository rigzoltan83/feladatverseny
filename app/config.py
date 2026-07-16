import os

from sqlalchemy import URL


def required_env(name: str) -> str:
    """Kötelező környezeti változó lekérése."""
    value = os.getenv(name)

    if value is None or value == "":
        raise RuntimeError(
            f"Hiányzó kötelező környezeti változó: {name}"
        )

    return value


class Config:
    SECRET_KEY = required_env("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="postgresql+psycopg",
        username=required_env("DB_USER"),
        password=required_env("DB_PASSWORD"),
        host=required_env("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=required_env("DB_NAME"),
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

    APP_TIMEZONE = os.getenv(
        "APP_TIMEZONE",
        "Europe/Budapest",
    )

    MEDIA_ROOT = os.getenv(
        "MEDIA_ROOT",
        "/srv/feladatverseny/media",
    )
