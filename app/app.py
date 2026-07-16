import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


def required_env(name: str) -> str:
    """Környezeti változó lekérése egyértelmű hibaüzenettel."""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Hiányzó kötelező környezeti változó: {name}")

    return value


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=required_env("DB_USER"),
    password=required_env("DB_PASSWORD"),
    host=required_env("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=required_env("DB_NAME"),
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

app = Flask(__name__)

app.config["SECRET_KEY"] = required_env("SECRET_KEY")

APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Europe/Budapest")


@app.get("/")
def index():
    return """
    <!doctype html>
    <html lang="hu">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Feladatverseny</title>
        <style>
            body {
                max-width: 800px;
                margin: 60px auto;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f4f6f8;
            }

            .card {
                padding: 30px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            }

            h1 {
                margin-top: 0;
            }

            .status {
                font-weight: bold;
                color: #176b32;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Feladatverseny</h1>
            <p class="status">A webalkalmazás működik.</p>
            <p>
                Adatbázis-ellenőrzés:
                <a href="/health">/health</a>
            </p>
        </div>
    </body>
    </html>
    """


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT
                        current_database() AS database_name,
                        current_user AS database_user,
                        current_setting('TimeZone') AS database_timezone,
                        now() AS database_time
                    """
                )
            ).mappings().one()

        local_time = datetime.now(ZoneInfo(APP_TIMEZONE))

        return jsonify(
            status="ok",
            application="feladatverseny",
            application_timezone=APP_TIMEZONE,
            application_time=local_time.isoformat(),
            database={
                "status": "ok",
                "name": result["database_name"],
                "user": result["database_user"],
                "timezone": result["database_timezone"],
                "time": result["database_time"].isoformat(),
            },
        )

    except SQLAlchemyError:
        app.logger.exception("Adatbázis-kapcsolati hiba")

        return jsonify(
            status="error",
            database={
                "status": "unavailable",
                "message": "Az adatbázis-kapcsolat nem érhető el.",
            },
        ), 503
