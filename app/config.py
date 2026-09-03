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

    BABEL_DEFAULT_LOCALE = "hu"
    BABEL_DEFAULT_TIMEZONE = "Europe/Budapest"

    BABEL_TRANSLATION_DIRECTORIES = (
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "translations",
        )
    )

    LANGUAGES = {
        "hu": "Magyar",
        "en": "English",
    }

    APPLICATION_PREFIX = (
        os.getenv(
            "APPLICATION_PREFIX",
            "",
        )
        .strip()
        .rstrip("/")
    )

    APPLICATION_ROOT = (
        APPLICATION_PREFIX
        or "/"
    )

    SESSION_COOKIE_NAME = (
        "feladatverseny_session"
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_PATH = (
        APPLICATION_PREFIX
        or "/"
    )

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

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
