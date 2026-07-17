from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models import Competitor
from app.extensions import db

competitor_bp = Blueprint(
    "competitor",
    __name__,
    url_prefix="/versenyzo",
)


@competitor_bp.route(
    "/belepes",
    methods=["GET", "POST"],
)
def login():
    if session.get("competitor_id"):
        return redirect(
            url_for("competitor.dashboard")
        )

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        competitor = (
            Competitor.query
            .filter(
                Competitor.username.ilike(username)
            )
            .first()
        )

        if (
            competitor
            and competitor.is_active
            and competitor.check_password(password)
        ):
            session.clear()

            session["competitor_id"] = competitor.id
            session["competitor_name"] = competitor.full_name

            flash(
                "Sikeres bejelentkezés.",
                "success",
            )

            return redirect(
                url_for("competitor.dashboard")
            )

        flash(
            "Hibás felhasználónév vagy jelszó.",
            "error",
        )

    return render_template(
        "competitor/login.html",
    )


@competitor_bp.get("/kijelentkezes")
def logout():
    session.clear()

    flash(
        "Sikeresen kijelentkeztél.",
        "success",
    )

    return redirect(
        url_for("competitor.login")
    )


@competitor_bp.get("/")
def dashboard():
    competitor_id = session.get(
        "competitor_id"
    )

    if not competitor_id:
        flash(
            "Az oldal megtekintéséhez jelentkezz be.",
            "error",
        )

        return redirect(
            url_for("competitor.login")
        )

    competitor = Competitor.query.get(
        competitor_id
    )

    if not competitor or not competitor.is_active:
        session.clear()

        flash(
            "A felhasználói fiók nem érhető el.",
            "error",
        )

        return redirect(
            url_for("competitor.login")
        )

    return render_template(
        "competitor/dashboard.html",
        competitor=competitor,
    )

