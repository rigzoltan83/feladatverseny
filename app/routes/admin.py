from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from pathlib import Path
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

def get_question_image_path(question: Question) -> Path:
    return (
        Path(current_app.config["MEDIA_ROOT"])
        / "questions"
        / question.image_filename
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

    topic_list = (
        Topic.query
        .filter_by(is_active=True)
        .order_by(Topic.name)
        .all()
    )

    source_year_list = (
        SourceYear.query
        .filter_by(is_active=True)
        .order_by(SourceYear.year_number.desc())
        .all()
    )

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
            request.form.get(
                f"answer_{position}",
                "",
            ).strip()
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

        if any(
            not answer_text
            for answer_text in answer_texts
        ):
            errors.append(
                "Mind az öt válaszlehetőséget ki kell tölteni."
            )

        if correct_answer not in range(1, 6):
            errors.append(
                "Ki kell választani a helyes választ."
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
                        is_correct=(
                            position == correct_answer
                        ),
                    )
                )

            db.session.add(question)
            db.session.commit()

            flash(
                (
                    "A feladatot és az öt "
                    "válaszlehetőséget elmentettük."
                ),
                "success",
            )

            return redirect(
                url_for("admin.questions")
            )

    return render_template(
        "admin/question_form.html",
        question=None,
        grades=grade_list,
        topics=topic_list,
        source_years=source_year_list,
        selected_grade_ids=set(),
        selected_topic_ids=set(),
        answer_by_position={},
    )


@admin_bp.get("/questions/<int:question_id>")
def question_detail(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    image_path = get_question_image_path(question)

    return render_template(
        "admin/question_detail.html",
        question=question,
        image_exists=image_path.is_file(),
    )

@admin_bp.route(
    "/questions/<int:question_id>/edit",
    methods=["GET", "POST"],
)
def question_edit(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    topic_list = (
        Topic.query
        .filter_by(is_active=True)
        .order_by(Topic.name)
        .all()
    )

    source_year_list = (
        SourceYear.query
        .filter_by(is_active=True)
        .order_by(SourceYear.year_number.desc())
        .all()
    )

    existing_answers = sorted(
        question.answer_options,
        key=lambda answer: answer.original_position,
    )

    answer_by_position = {
        answer.original_position: answer
        for answer in existing_answers
    }

    selected_grade_ids = {
        grade.id
        for grade in question.grades
    }

    selected_topic_ids = {
        topic.id
        for topic in question.topics
    }

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

        posted_grade_ids = request.form.getlist(
            "grade_ids",
            type=int,
        )

        posted_topic_ids = request.form.getlist(
            "topic_ids",
            type=int,
        )

        answer_texts = [
            request.form.get(
                f"answer_{position}",
                "",
            ).strip()
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

        if not posted_grade_ids:
            errors.append(
                "Legalább egy évfolyamot ki kell választani."
            )

        if not posted_topic_ids:
            errors.append(
                "Legalább egy témakört ki kell választani."
            )

        if any(
            not answer_text
            for answer_text in answer_texts
        ):
            errors.append(
                "Mind az öt válaszlehetőséget ki kell tölteni."
            )

        if correct_answer not in range(1, 6):
            errors.append(
                "Ki kell választani a helyes választ."
            )

        selected_grades = Grade.query.filter(
            Grade.id.in_(posted_grade_ids)
        ).all()

        selected_topics = Topic.query.filter(
            Topic.id.in_(posted_topic_ids)
        ).all()

        if len(selected_grades) != len(
            set(posted_grade_ids)
        ):
            errors.append(
                "Az évfolyamválasztás érvénytelen."
            )

        if len(selected_topics) != len(
            set(posted_topic_ids)
        ):
            errors.append(
                "A témakörválasztás érvénytelen."
            )

        if errors:
            for error in errors:
                flash(error, "error")

        else:
            question.source_year = source_year
            question.original_position = original_position
            question.difficulty = difficulty
            question.question_text = question_text
            question.explanation = explanation or None
            question.grades = selected_grades
            question.topics = selected_topics

            AnswerOption.query.filter_by(
                question_id=question.id
            ).delete(
                synchronize_session=False
            )

            db.session.flush()

            for position, answer_text in enumerate(
                answer_texts,
                start=1,
            ):
                db.session.add(
                    AnswerOption(
                        question_id=question.id,
                        original_position=position,
                        answer_text=answer_text,
                        is_correct=(
                            position == correct_answer
                        ),
                    )
                )

            # Fontos: ez már a cikluson kívül van.
            db.session.commit()

            flash(
                "A feladat módosításait elmentettük.",
                "success",
            )

            return redirect(
                url_for(
                    "admin.question_detail",
                    question_id=question.id,
                )
            )

    return render_template(
        "admin/question_form.html",
        question=question,
        grades=grade_list,
        topics=topic_list,
        source_years=source_year_list,
        selected_grade_ids=selected_grade_ids,
        selected_topic_ids=selected_topic_ids,
        answer_by_position=answer_by_position,
    )

@admin_bp.get("/media/questions/<path:filename>")
def question_image(filename: str):
    media_root = current_app.config["MEDIA_ROOT"]

    return send_from_directory(
        f"{media_root}/questions",
        filename,
    )

@admin_bp.post("/questions/<int:question_id>/image")
def question_image_upload(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    uploaded_file = request.files.get("image")

    if uploaded_file is None or not uploaded_file.filename:
        flash(
            "Nem választottál ki képfájlt.",
            "error",
        )

        return redirect(
            url_for(
                "admin.question_detail",
                question_id=question.id,
            )
        )

    filename_lower = uploaded_file.filename.lower()

    if not filename_lower.endswith((".jpg", ".jpeg")):
        flash(
            "Csak JPG vagy JPEG kép tölthető fel.",
            "error",
        )

        return redirect(
            url_for(
                "admin.question_detail",
                question_id=question.id,
            )
        )

    image_path = get_question_image_path(question)

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    uploaded_file.save(image_path)

    flash(
        f"A kép feltöltve: {question.image_filename}",
        "success",
    )

    return redirect(
        url_for(
            "admin.question_detail",
            question_id=question.id,
        )
    )

@admin_bp.post("/questions/<int:question_id>/image/delete")
def question_image_delete(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    image_path = get_question_image_path(question)

    if image_path.is_file():
        image_path.unlink()

        flash(
            "A feladat képét töröltük.",
            "success",
        )
    else:
        flash(
            "A feladathoz nem tartozik kép.",
            "error",
        )

    return redirect(
        url_for(
            "admin.question_detail",
            question_id=question.id,
        )
    )
