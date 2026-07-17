import os

from dotenv import load_dotenv
from flask import Flask


def create_app() -> Flask:
    """A Flask alkalmazás létrehozása."""

    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    load_dotenv(
        os.path.join(project_root, ".env")
    )

    # A Config csak a .env betöltése után importálható.
    from app.config import Config
    from app.extensions import db, migrate

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes.admin import admin_bp
    from app.routes.competitor import competitor_bp
    from app.routes.admin_reference import reference_bp
    from app.routes.admin_media import media_bp
    from app.routes.admin_templates import template_bp
    from app.routes.admin_generated_tests import (
        generated_test_bp,
    )
    app.register_blueprint(admin_bp)
    app.register_blueprint(competitor_bp)
    app.register_blueprint(reference_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(generated_test_bp)

    register_routes(app)

    return app


def register_routes(app: Flask) -> None:
    """Az első tesztútvonalak regisztrálása."""

    from datetime import datetime
    from zoneinfo import ZoneInfo

    from flask import current_app, jsonify
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError

    from app.extensions import db

    @app.get("/")
    def index():
        return "A Feladatverseny alkalmazás működik."

    @app.get("/health")
    def health():
        try:
            result = db.session.execute(
                text(
                    """
                    SELECT
                        current_database() AS database_name,
                        current_user AS database_user,
                        current_setting('TimeZone')
                            AS database_timezone,
                        now() AS database_time
                    """
                )
            ).mappings().one()

            timezone_name = current_app.config[
                "APP_TIMEZONE"
            ]

            application_time = datetime.now(
                ZoneInfo(timezone_name)
            )

            return jsonify(
                status="ok",
                application="feladatverseny",
                application_timezone=timezone_name,
                application_time=application_time.isoformat(),
                database={
                    "status": "ok",
                    "name": result["database_name"],
                    "user": result["database_user"],
                    "timezone": result[
                        "database_timezone"
                    ],
                    "time": result[
                        "database_time"
                    ].isoformat(),
                },
            )

        except SQLAlchemyError:
            current_app.logger.exception(
                "Adatbázis-kapcsolati hiba"
            )

            db.session.rollback()

            return jsonify(
                status="error",
                database={
                    "status": "unavailable",
                    "message": (
                        "Az adatbázis-kapcsolat "
                        "nem érhető el."
                    ),
                },
            ), 503
