from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models import (
    Grade,
    TestTemplate,
    Topic,
)


template_bp = Blueprint(
    "admin_templates",
    __name__,
    url_prefix="/admin/test-templates",
)


@template_bp.get("/")
def template_list():
    templates = (
        TestTemplate.query
        .order_by(
            TestTemplate.is_active.desc(),
            TestTemplate.name,
        )
        .all()
    )

    return render_template(
        "admin/test_templates.html",
        templates=templates,
    )


@template_bp.route(
    "/new",
    methods=["GET", "POST"],
)
def template_new():
    grades = Grade.query.order_by(
        Grade.grade_number
    ).all()

    topics = (
        Topic.query
        .filter_by(is_active=True)
        .order_by(Topic.name)
        .all()
    )

    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        question_count = request.form.get(
            "question_count",
            type=int,
        )

        grade_ids = request.form.getlist(
            "grade_ids",
            type=int,
        )

        topic_ids = request.form.getlist(
            "topic_ids",
            type=int,
        )

        shuffle_questions = (
            request.form.get(
                "shuffle_questions"
            )
            == "on"
        )

        shuffle_answers = (
            request.form.get(
                "shuffle_answers"
            )
            == "on"
        )

        errors = []

        if not name:
            errors.append(
                "A tesztsablon neve kötelező."
            )

        existing_template = (
            TestTemplate.query
            .filter(
                db.func.lower(
                    TestTemplate.name
                )
                == name.lower()
            )
            .first()
        )

        if existing_template is not None:
            errors.append(
                (
                    "Már létezik ilyen nevű "
                    "tesztsablon."
                )
            )

        if (
            question_count is None
            or not 1 <= question_count <= 100
        ):
            errors.append(
                (
                    "A feladatok száma "
                    "1 és 100 közötti lehet."
                )
            )

        if not grade_ids:
            errors.append(
                (
                    "Legalább egy évfolyamot "
                    "ki kell választani."
                )
            )

        if not topic_ids:
            errors.append(
                (
                    "Legalább egy témakört "
                    "ki kell választani."
                )
            )

        selected_grades = Grade.query.filter(
            Grade.id.in_(grade_ids)
        ).all()

        selected_topics = Topic.query.filter(
            Topic.id.in_(topic_ids)
        ).all()

        if len(selected_grades) != len(
            set(grade_ids)
        ):
            errors.append(
                "Az évfolyamválasztás érvénytelen."
            )

        if len(selected_topics) != len(
            set(topic_ids)
        ):
            errors.append(
                "A témakörválasztás érvénytelen."
            )

        if errors:
            for error in errors:
                flash(
                    error,
                    "error",
                )

        else:
            template = TestTemplate(
                name=name,
                description=(
                    description or None
                ),
                question_count=question_count,
                shuffle_questions=(
                    shuffle_questions
                ),
                shuffle_answers=(
                    shuffle_answers
                ),
                is_active=True,
            )

            template.grades = selected_grades
            template.topics = selected_topics

            db.session.add(template)
            db.session.commit()

            flash(
                "A tesztsablont létrehoztuk.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_templates.template_list"
                )
            )

    return render_template(
        "admin/test_template_form.html",
        template=None,
        grades=grades,
        topics=topics,
        selected_grade_ids=set(),
        selected_topic_ids=set(),
    )

@template_bp.get("/<int:template_id>")
def template_detail(template_id: int):
    template = db.get_or_404(
        TestTemplate,
        template_id,
    )

    return render_template(
        "admin/test_template_detail.html",
        template=template,
    )


@template_bp.route(
    "/<int:template_id>/edit",
    methods=["GET", "POST"],
)
def template_edit(template_id: int):
    template = db.get_or_404(
        TestTemplate,
        template_id,
    )

    grades = Grade.query.order_by(
        Grade.grade_number
    ).all()

    topics = (
        Topic.query
        .filter_by(is_active=True)
        .order_by(Topic.name)
        .all()
    )

    selected_grade_ids = {
        grade.id
        for grade in template.grades
    }

    selected_topic_ids = {
        topic.id
        for topic in template.topics
    }

    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        question_count = request.form.get(
            "question_count",
            type=int,
        )

        grade_ids = request.form.getlist(
            "grade_ids",
            type=int,
        )

        topic_ids = request.form.getlist(
            "topic_ids",
            type=int,
        )

        shuffle_questions = (
            request.form.get(
                "shuffle_questions"
            )
            == "on"
        )

        shuffle_answers = (
            request.form.get(
                "shuffle_answers"
            )
            == "on"
        )

        errors = []

        if not name:
            errors.append(
                "A tesztsablon neve kötelező."
            )

        duplicate_template = (
            TestTemplate.query
            .filter(
                db.func.lower(
                    TestTemplate.name
                )
                == name.lower(),
                TestTemplate.id != template.id,
            )
            .first()
        )

        if duplicate_template is not None:
            errors.append(
                (
                    "Már létezik ilyen nevű "
                    "tesztsablon."
                )
            )

        if (
            question_count is None
            or not 1 <= question_count <= 100
        ):
            errors.append(
                (
                    "A feladatok száma "
                    "1 és 100 közötti lehet."
                )
            )

        if not grade_ids:
            errors.append(
                (
                    "Legalább egy évfolyamot "
                    "ki kell választani."
                )
            )

        if not topic_ids:
            errors.append(
                (
                    "Legalább egy témakört "
                    "ki kell választani."
                )
            )

        selected_grades = Grade.query.filter(
            Grade.id.in_(grade_ids)
        ).all()

        selected_topics = Topic.query.filter(
            Topic.id.in_(topic_ids)
        ).all()

        if len(selected_grades) != len(
            set(grade_ids)
        ):
            errors.append(
                "Az évfolyamválasztás érvénytelen."
            )

        if len(selected_topics) != len(
            set(topic_ids)
        ):
            errors.append(
                "A témakörválasztás érvénytelen."
            )

        if errors:
            for error in errors:
                flash(
                    error,
                    "error",
                )

        else:
            template.name = name
            template.description = (
                description or None
            )
            template.question_count = question_count
            template.shuffle_questions = (
                shuffle_questions
            )
            template.shuffle_answers = (
                shuffle_answers
            )
            template.grades = selected_grades
            template.topics = selected_topics

            db.session.commit()

            flash(
                (
                    "A tesztsablon módosításait "
                    "elmentettük."
                ),
                "success",
            )

            return redirect(
                url_for(
                    "admin_templates.template_detail",
                    template_id=template.id,
                )
            )

    return render_template(
        "admin/test_template_form.html",
        template=template,
        grades=grades,
        topics=topics,
        selected_grade_ids=selected_grade_ids,
        selected_topic_ids=selected_topic_ids,
    )


@template_bp.post(
    "/<int:template_id>/toggle-active"
)
def template_toggle_active(template_id: int):
    template = db.get_or_404(
        TestTemplate,
        template_id,
    )

    template.is_active = not template.is_active

    db.session.commit()

    if template.is_active:
        message = "A tesztsablont aktiváltuk."
    else:
        message = "A tesztsablont inaktiváltuk."

    flash(
        message,
        "success",
    )

    return redirect(
        url_for(
            "admin_templates.template_detail",
            template_id=template.id,
        )
    )
