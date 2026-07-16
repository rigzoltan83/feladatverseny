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
    AnswerOption,
    Grade,
    Question,
    SourceYear,
    Topic,
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


@admin_bp.get("/")
def index():
    return render_template("admin/index.html")


@admin_bp.get("/grades")
def grades():
    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    return render_template(
        "admin/grades.html",
        grades=grade_list,
    )

@admin_bp.get("/topics")
def topics():
    topic_list = Topic.query.order_by(
        Topic.name
    ).all()

    return render_template(
        "admin/topics.html",
        topics=topic_list,
    )

@admin_bp.get("/source-years")
def source_years():
    source_year_list = SourceYear.query.order_by(
        SourceYear.year_number.desc()
    ).all()

    return render_template(
        "admin/source_years.html",
        source_years=source_year_list,
    )

@admin_bp.get("/questions")
def questions():
    question_list = (
        Question.query
        .order_by(
            Question.source_year_id.desc(),
            Question.original_position.asc(),
        )
        .all()
    )

    return render_template(
        "admin/questions.html",
        questions=question_list,
    )

@admin_bp.route("/questions/new", methods=["GET", "POST"])
def question_new():
    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    topic_list = Topic.query.filter_by(
        is_active=True
    ).order_by(
        Topic.name
    ).all()

    source_year_list = SourceYear.query.filter_by(
        is_active=True
    ).order_by(
        SourceYear.year_number.desc()
    ).all()

    if request.method == "POST":
        source_year_id = request.form.get(
            "source_year_id",
            type=int,
        )

        original_position = request.form.get(
            "original_position",
            type=int,
        )

        difficulty = request.form.get(
            "difficulty",
            type=int,
        )

        question_text = request.form.get(
            "question_text",
            "",
        ).strip()

        explanation = request.form.get(
            "explanation",
            "",
        ).strip()

        selected_grade_ids = request.form.getlist(
            "grade_ids",
            type=int,
        )

        selected_topic_ids = request.form.getlist(
            "topic_ids",
            type=int,
        )

        answer_texts = [
            request.form.get(f"answer_{position}", "").strip()
            for position in range(1, 6)
        ]

        correct_answer = request.form.get(
            "correct_answer",
            type=int,
        )

        errors = []

        source_year = db.session.get(
            SourceYear,
            source_year_id,
        )

        if source_year is None:
            errors.append(
                "Érvényes forrásévet kell választani."
            )

        if (
            original_position is None
            or not 1 <= original_position <= 25
        ):
            errors.append(
                "A feladat sorszáma 1 és 25 közötti lehet."
            )

        if (
            difficulty is None
            or not 1 <= difficulty <= 25
        ):
            errors.append(
                "A nehézség 1 és 25 közötti lehet."
            )

        if not question_text:
            errors.append(
                "A feladat szövege kötelező."
            )

        if not selected_grade_ids:
            errors.append(
                "Legalább egy évfolyamot ki kell választani."
            )

        if not selected_topic_ids:
            errors.append(
                "Legalább egy témakört ki kell választani."
            )

        selected_grades = Grade.query.filter(
            Grade.id.in_(selected_grade_ids)
        ).all()

        selected_topics = Topic.query.filter(
            Topic.id.in_(selected_topic_ids)
        ).all()

        if len(selected_grades) != len(
            set(selected_grade_ids)
        ):
            errors.append(
                "Az évfolyamválasztás érvénytelen."
            )

        if len(selected_topics) != len(
            set(selected_topic_ids)
        ):
            errors.append(
                "A témakörválasztás érvénytelen."
            )

        if any(not answer_text for answer_text in answer_texts):
            errors.append(
                "Mind az öt válaszlehetőséget ki kell tölteni."
            )

        if correct_answer not in range(1, 6):
            errors.append(
                "Ki kell választani a helyes választ."
            )

        if errors:
            for error in errors:
                flash(error, "error")

        else:
            question = Question(
                source_year=source_year,
                original_position=original_position,
                difficulty=difficulty,
                question_text=question_text,
                explanation=explanation or None,
                is_active=True,
            )

            question.grades = selected_grades
            question.topics = selected_topics

            for position, answer_text in enumerate(
                answer_texts,
                start=1,
            ):
                question.answer_options.append(
                    AnswerOption(
                        original_position=position,
                        answer_text=answer_text,
                        is_correct=(position == correct_answer),
                    )
                )

            db.session.add(question)
            db.session.commit()

            flash(
                "A feladatot és az öt válaszlehetőséget elmentettük.",
                "success",
            )

            return redirect(
                url_for("admin.questions")
            )

    return render_template(
        "admin/question_form.html",
        grades=grade_list,
        topics=topic_list,
        source_years=source_year_list,
    )
