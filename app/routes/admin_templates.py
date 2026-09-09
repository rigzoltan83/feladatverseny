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
from app.models import (
    Grade,
    Question,
    SourceYear,
    TestTemplate,
    TestTemplateQuestion,
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

        selection_mode = request.form.get(
            "selection_mode",
            "automatic",
        ).strip()

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

        if selection_mode not in {
            "automatic",
            "manual",
        }:
            errors.append(
                _("Az összeállítás módja érvénytelen.")
            )

        if not name:
            errors.append(
                _("A tesztsablon neve kötelező.")
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
                    _(
                    "Már létezik ilyen nevű "
                    "tesztsablon."
                )
                )
            )

        if (
            question_count is None
            or not 1 <= question_count <= 100
        ):
            errors.append(
                (
                    _(
                    "A feladatok száma "
                    "1 és 100 közötti lehet."
                )
                )
            )

        if selection_mode == "automatic":
            if not grade_ids:
                errors.append(
                    _(
                        "Legalább egy évfolyamot "
                        "ki kell választani."
                    )
                )

            if not topic_ids:
                errors.append(
                    _(
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
                _("Az évfolyamválasztás érvénytelen.")
            )

        if len(selected_topics) != len(
            set(topic_ids)
        ):
            errors.append(
                _("A témakörválasztás érvénytelen.")
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
                selection_mode=selection_mode,
                shuffle_questions=(
                    shuffle_questions
                    if selection_mode == "automatic"
                    else False
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
                _("A tesztsablont létrehoztuk."),
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

    if template.selection_mode == "manual":
        manual_questions = (
            TestTemplateQuestion.query
            .filter_by(
                test_template_id=template.id,
            )
            .order_by(
                TestTemplateQuestion.display_position
            )
            .all()
        )

        available_question_count = len(
            manual_questions
        )

        enough_questions = (
            available_question_count > 0
        )

        return render_template(
            "admin/test_template_detail.html",
            template=template,
            available_question_count=(
                available_question_count
            ),
            enough_questions=enough_questions,
            sample_questions=[],
            manual_questions=manual_questions,
        )

    grade_ids = [
        grade.id
        for grade in template.grades
    ]

    topic_ids = [
        topic.id
        for topic in template.topics
    ]

    candidate_query = Question.query.filter(
        Question.is_active.is_(True)
    )

    if grade_ids:
        candidate_query = candidate_query.filter(
            Question.grades.any(
                Grade.id.in_(grade_ids)
            )
        )
    else:
        candidate_query = candidate_query.filter(
            db.false()
        )

    if topic_ids:
        candidate_query = candidate_query.filter(
            Question.topics.any(
                Topic.id.in_(topic_ids)
            )
        )
    else:
        candidate_query = candidate_query.filter(
            db.false()
        )

    available_question_count = (
        candidate_query.count()
    )

    enough_questions = (
        available_question_count
        >= template.question_count
    )

    sample_questions = (
        candidate_query
        .order_by(
            Question.difficulty,
            Question.id,
        )
        .limit(10)
        .all()
    )

    return render_template(
        "admin/test_template_detail.html",
        template=template,
        available_question_count=(
            available_question_count
        ),
        enough_questions=enough_questions,
        sample_questions=sample_questions,
        manual_questions=[],
    )


@template_bp.route(
    "/<int:template_id>/questions",
    methods=["GET", "POST"],
)
def template_questions(template_id: int):
    template = db.get_or_404(
        TestTemplate,
        template_id,
    )

    if template.selection_mode != "manual":
        flash(
            _(
                "Kézi feladatválasztás csak manuális "
                "tesztsablonnál használható."
            ),
            "error",
        )

        return redirect(
            url_for(
                "admin_templates.template_detail",
                template_id=template.id,
            )
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

    source_years = (
        SourceYear.query
        .order_by(
            SourceYear.year_number.desc()
        )
        .all()
    )

    if request.method == "POST":
        question_ids = request.form.getlist(
            "question_ids",
            type=int,
        )

        question_ids = list(
            dict.fromkeys(question_ids)
        )

        if not question_ids:
            flash(
                _(
                    "Legalább egy feladatot "
                    "ki kell választani."
                ),
                "error",
            )
        elif len(question_ids) > 100:
            flash(
                _(
                    "Legfeljebb 100 feladat "
                    "választható ki."
                ),
                "error",
            )
        else:
            selected_questions = (
                Question.query
                .filter(
                    Question.id.in_(question_ids),
                    Question.is_active.is_(True),
                )
                .all()
            )

            selected_by_id = {
                question.id: question
                for question in selected_questions
            }

            if len(selected_by_id) != len(
                question_ids
            ):
                flash(
                    _(
                        "A kiválasztott feladatok között "
                        "érvénytelen vagy inaktív feladat "
                        "található."
                    ),
                    "error",
                )
            else:
                existing_rows = (
                    TestTemplateQuestion.query
                    .filter_by(
                        test_template_id=template.id,
                    )
                    .all()
                )

                for row in existing_rows:
                    db.session.delete(row)

                db.session.flush()

                for position, question_id in enumerate(
                    question_ids,
                    start=1,
                ):
                    db.session.add(
                        TestTemplateQuestion(
                            test_template_id=template.id,
                            question_id=question_id,
                            display_position=position,
                        )
                    )

                template.question_count = len(
                    question_ids
                )

                db.session.commit()

                flash(
                    _(
                        "A manuális feladatsor "
                        "kiválasztását elmentettük."
                    ),
                    "success",
                )

                return redirect(
                    url_for(
                        "admin_templates.template_detail",
                        template_id=template.id,
                    )
                )

    search_text = request.args.get(
        "q",
        "",
    ).strip()

    selected_grade_id = request.args.get(
        "grade_id",
        0,
        type=int,
    )

    selected_topic_id = request.args.get(
        "topic_id",
        0,
        type=int,
    )

    selected_source_year_id = request.args.get(
        "source_year_id",
        0,
        type=int,
    )

    question_query = Question.query.filter(
        Question.is_active.is_(True)
    )

    if search_text:
        question_query = question_query.filter(
            Question.question_text.ilike(
                f"%{search_text}%"
            )
        )

    if selected_grade_id:
        question_query = question_query.filter(
            Question.grades.any(
                Grade.id == selected_grade_id
            )
        )

    if selected_topic_id:
        question_query = question_query.filter(
            Question.topics.any(
                Topic.id == selected_topic_id
            )
        )

    if selected_source_year_id:
        question_query = question_query.filter(
            Question.source_year_id
            == selected_source_year_id
        )

    questions = (
        question_query
        .order_by(
            Question.difficulty,
            Question.id,
        )
        .all()
    )

    selected_question_ids = {
        row.question_id
        for row in template.manual_questions
    }

    return render_template(
        "admin/test_template_questions.html",
        template=template,
        questions=questions,
        grades=grades,
        topics=topics,
        source_years=source_years,
        search_text=search_text,
        selected_grade_id=selected_grade_id,
        selected_topic_id=selected_topic_id,
        selected_source_year_id=(
            selected_source_year_id
        ),
        selected_question_ids=(
            selected_question_ids
        ),
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

        selection_mode = request.form.get(
            "selection_mode",
            template.selection_mode,
        ).strip()

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

        if selection_mode not in {
            "automatic",
            "manual",
        }:
            errors.append(
                _("Az összeállítás módja érvénytelen.")
            )

        if not name:
            errors.append(
                _("A tesztsablon neve kötelező.")
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
                    _(
                    "Már létezik ilyen nevű "
                    "tesztsablon."
                )
                )
            )

        if (
            question_count is None
            or not 1 <= question_count <= 100
        ):
            errors.append(
                (
                    _(
                    "A feladatok száma "
                    "1 és 100 közötti lehet."
                )
                )
            )

        if selection_mode == "automatic":
            if not grade_ids:
                errors.append(
                    _(
                        "Legalább egy évfolyamot "
                        "ki kell választani."
                    )
                )

            if not topic_ids:
                errors.append(
                    _(
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
                _("Az évfolyamválasztás érvénytelen.")
            )

        if len(selected_topics) != len(
            set(topic_ids)
        ):
            errors.append(
                _("A témakörválasztás érvénytelen.")
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
            template.selection_mode = selection_mode
            template.shuffle_questions = (
                shuffle_questions
                if selection_mode == "automatic"
                else False
            )
            template.shuffle_answers = (
                shuffle_answers
            )
            template.grades = selected_grades
            template.topics = selected_topics

            db.session.commit()

            flash(
                (
                    _(
                    "A tesztsablon módosításait "
                    "elmentettük."
                )
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
        message = _(
            "A tesztsablont aktiváltuk."
        )
    else:
        message = _(
            "A tesztsablont inaktiváltuk."
        )

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
