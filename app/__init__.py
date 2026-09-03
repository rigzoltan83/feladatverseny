import os

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    request,
    session,
    url_for,
)

from flask_babel import (
    get_locale,
    gettext as _,
)

def create_app() -> Flask:
    """Create and configure the Flask application."""

    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    load_dotenv(
        os.path.join(project_root, ".env")
    )

    # Config must be imported only after loading .env.
    from app.config import Config
    from app.extensions import babel, db, migrate

    app = Flask(__name__)
    app.config.from_object(Config)

    application_prefix = app.config[
        "APPLICATION_PREFIX"
    ]

    if application_prefix:
        original_wsgi_app = app.wsgi_app

        def prefixed_wsgi_app(
            environ,
            start_response,
        ):
            environ[
                "SCRIPT_NAME"
            ] = application_prefix

            return original_wsgi_app(
                environ,
                start_response,
            )

        app.wsgi_app = prefixed_wsgi_app

    db.init_app(app)

    migrate.init_app(app, db)

    from app import models

    def select_locale():
        selected_language = session.get(
            "language"
        )

        if selected_language in app.config["LANGUAGES"]:
            return selected_language

        competitor_id = session.get(
            "competitor_id"
        )

        if competitor_id:
            competitor = db.session.get(
                models.Competitor,
                competitor_id,
            )

            if (
                competitor is not None
                and competitor.preferred_language
                in app.config["LANGUAGES"]
            ):
                selected_language = (
                    competitor.preferred_language
                )

                session["language"] = (
                    selected_language
                )

                return selected_language

        cookie_language = request.cookies.get(
            "feladatverseny_language"
        )

        if cookie_language in app.config["LANGUAGES"]:
            return cookie_language

        return app.config[
            "BABEL_DEFAULT_LOCALE"
        ]

    babel.init_app(
        app,
        locale_selector=select_locale,
    )

    app.jinja_env.globals[
        "get_locale"
    ] = get_locale

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

    @app.before_request
    def protect_admin_routes():
        if not request.path.startswith("/admin"):
            return None

        competitor_id = session.get(
            "competitor_id"
        )

        if not competitor_id:
            flash(
                _(
                    "Az adminisztráció használatához "
                    "jelentkezz be."
                ),
                "error",
            )

            return redirect(
                url_for("competitor.login")
            )

        competitor = db.session.get(
            models.Competitor,
            competitor_id,
        )

        if (
            competitor is None
            or not competitor.is_active
        ):
            session.clear()

            flash(
                _(
                    "A felhasználói fiók nem érhető el."
                ),
                "error",
            )

            return redirect(
                url_for("competitor.login")
            )

        if not competitor.is_admin:
            abort(403)

        session["is_admin"] = True

        return None

    register_routes(app)

    return app


def register_routes(app: Flask) -> None:
    """Register the application root and health routes."""

    from datetime import datetime
    from zoneinfo import ZoneInfo

    from flask import current_app, jsonify
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError

    from app.extensions import db

    @app.get("/")
    def index():
        return redirect(
            url_for("competitor.login")
        )

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
                "Database connection error"
            )

            db.session.rollback()

            return jsonify(
                status="error",
                database={
                    "status": "unavailable",
                    "message": (
                        "The database connection "
                        "is unavailable."
                    ),
                },
            ), 503
