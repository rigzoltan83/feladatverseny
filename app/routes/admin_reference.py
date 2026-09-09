from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import gettext as _

from app.extensions import db
from app.models import Grade, SourceYear, Topic


reference_bp = Blueprint(
    "admin_reference",
    __name__,
    url_prefix="/admin",
)


@reference_bp.get("/grades")
def grades():
    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    return render_template(
        "admin/grades.html",
        grades=grade_list,
    )


@reference_bp.route(
    "/topics",
    methods=["GET", "POST"],
)
def topics():
    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        name_en = request.form.get(
            "name_en",
            "",
        ).strip()

        errors = []

        if not name:
            errors.append(
                _("A témakör magyar neve kötelező.")
            )
        elif len(name) > 100:
            errors.append(
                _(
                    "A témakör magyar neve "
                    "legfeljebb 100 karakter lehet."
                )
            )

        if len(name_en) > 100:
            errors.append(
                _(
                    "A témakör angol neve "
                    "legfeljebb 100 karakter lehet."
                )
            )

        if name:
            existing_topic = (
                Topic.query
                .filter(
                    db.func.lower(Topic.name)
                    == name.lower()
                )
                .first()
            )

            if existing_topic is not None:
                errors.append(
                    _(
                        "Már létezik ilyen nevű "
                        "témakör."
                    )
                )

        if errors:
            for error in errors:
                flash(
                    error,
                    "error",
                )
        else:
            topic = Topic(
                name=name,
                name_en=name_en or None,
                is_active=True,
            )

            db.session.add(topic)
            db.session.commit()

            flash(
                _("A témakör sikeresen létrejött."),
                "success",
            )

            return redirect(
                url_for(
                    "admin_reference.topics"
                )
            )

    topic_list = Topic.query.order_by(
        Topic.name
    ).all()

    return render_template(
        "admin/topics.html",
        topics=topic_list,
    )


@reference_bp.get("/source-years")
def source_years():
    source_year_list = SourceYear.query.order_by(
        SourceYear.year_number.desc()
    ).all()

    return render_template(
        "admin/source_years.html",
        source_years=source_year_list,
    )
