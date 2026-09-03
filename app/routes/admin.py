import csv
import io

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_babel import gettext as _

from app.extensions import db
from app.models import (
    Competitor,
    CompetitorAttempt,
    AnswerOption,
    GeneratedTest,
    Grade,
    Question,
    SourceYear,
    Topic,
)

from app.routes.admin_media import (
    get_question_image_path,
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)

CSV_FIELDNAMES = [
    "forrasev",
    "sorszam",
    "nehezseg",
    "evfolyamok",
    "temakorok",
    "feladat",
    "valasz1",
    "valasz2",
    "valasz3",
    "valasz4",
    "valasz5",
    "helyes",
    "magyarazat",
    "aktiv",
]

def parse_boolean(value: str) -> bool | None:
    normalized = value.strip().lower()

    if normalized in {
        "igen",
        "true",
        "1",
        "yes",
        "aktív",
        "aktiv",
    }:
        return True

    if normalized in {
        "nem",
        "false",
        "0",
        "no",
        "inaktív",
        "inaktiv",
    }:
        return False

    return None

@admin_bp.get("/")
def index():
    return render_template(
        "admin/index.html"
    )

@admin_bp.get("/results")
def results():
    closed_tests = (
        GeneratedTest.query
        .filter_by(status="closed")
        .order_by(GeneratedTest.id.desc())
        .all()
    )

    result_rows = []

    for generated_test in closed_tests:
        attempts = (
            generated_test
            .competitor_attempts
            .all()
        )

        submitted_attempts = [
            attempt
            for attempt in attempts
            if attempt.status == "submitted"
        ]

        scores = []

        for attempt in submitted_attempts:
            score = sum(
                1
                for competitor_answer in attempt.answers
                if (
                    competitor_answer
                    .generated_test_answer
                    .answer_option
                    .is_correct
                )
            )

            scores.append(score)

        average_score = (
            sum(scores) / len(scores)
            if scores
            else None
        )

        best_score = (
            max(scores)
            if scores
            else None
        )

        result_rows.append(
            {
                "generated_test": generated_test,
                "question_count": len(
                    generated_test.generated_questions
                ),
                "attempt_count": len(attempts),
                "submitted_count": len(
                    submitted_attempts
                ),
                "average_score": average_score,
                "best_score": best_score,
            }
        )

    return render_template(
        "admin/results.html",
        result_rows=result_rows,
    )

@admin_bp.get(
    "/results/<int:generated_test_id>"
)
def result_detail(
    generated_test_id: int,
):
    generated_test = db.get_or_404(
        GeneratedTest,
        generated_test_id,
    )

    if generated_test.status != "closed":
        abort(404)

    question_count = len(
        generated_test.generated_questions
    )

    attempts = (
        generated_test
        .competitor_attempts
        .all()
    )

    result_rows = []

    for attempt in attempts:
        score = sum(
            1
            for competitor_answer in attempt.answers
            if (
                competitor_answer
                .generated_test_answer
                .answer_option
                .is_correct
            )
        )

        percentage = (
            score / question_count * 100
            if question_count
            else 0
        )

        duration_text = None

        if (
            attempt.submitted_at is not None
            and attempt.started_at is not None
        ):
            duration_seconds = int(
                (
                    attempt.submitted_at
                    - attempt.started_at
                ).total_seconds()
            )

            duration_seconds = max(
                duration_seconds,
                0,
            )

            duration_minutes, seconds = divmod(
                duration_seconds,
                60,
            )

            hours, minutes = divmod(
                duration_minutes,
                60,
            )

            if hours:
                duration_text = _(
                    "%(hours)s h %(minutes)s min "
                    "%(seconds)s sec",
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                )
            elif minutes:
                duration_text = _(
                    "%(minutes)s min %(seconds)s sec",
                    minutes=minutes,
                    seconds=seconds,
                )
            else:
                duration_text = _(
                    "%(seconds)s sec",
                    seconds=seconds,
                )

        result_rows.append(
            {
                "attempt": attempt,
                "score": score,
                "percentage": percentage,
                "duration_text": duration_text,
            }
        )

    result_rows.sort(
        key=lambda row: (
            row["attempt"].status
            != "submitted",
            -row["score"],
            row["attempt"].competitor.full_name.lower(),
        )
    )

    current_rank = 0
    previous_score = None

    for row_number, row in enumerate(
        result_rows,
        start=1,
    ):
        if row["attempt"].status != "submitted":
            row["rank"] = None
            continue

        if row["score"] != previous_score:
            current_rank = row_number
            previous_score = row["score"]

        row["rank"] = current_rank

    submitted_count = sum(
        1
        for row in result_rows
        if row["attempt"].status == "submitted"
    )

    return render_template(
        "admin/result_detail.html",
        generated_test=generated_test,
        question_count=question_count,
        result_rows=result_rows,
        submitted_count=submitted_count,
    )

@admin_bp.get(
    "/results/attempt/<int:attempt_id>"
)
def attempt_result_detail(
    attempt_id: int,
):
    attempt = db.get_or_404(
        CompetitorAttempt,
        attempt_id,
    )

    generated_test = attempt.generated_test

    if generated_test.status != "closed":
        abort(404)

    generated_questions = sorted(
        generated_test.generated_questions,
        key=lambda question: question.display_position,
    )

    saved_answers = {
        competitor_answer.generated_test_question_id:
            competitor_answer.generated_test_answer_id
        for competitor_answer in attempt.answers
    }

    correct_answer_count = 0
    question_results = []

    for generated_question in generated_questions:
        selected_answer_id = saved_answers.get(
            generated_question.id
        )

        selected_answer = next(
            (
                generated_answer
                for generated_answer
                in generated_question.generated_answers
                if generated_answer.id
                == selected_answer_id
            ),
            None,
        )

        is_correct = (
            selected_answer is not None
            and selected_answer.answer_option.is_correct
        )

        if is_correct:
            correct_answer_count += 1

        question_results.append(
            {
                "generated_question":
                    generated_question,
                "selected_answer_id":
                    selected_answer_id,
                "is_correct":
                    is_correct,
            }
        )

    question_count = len(generated_questions)

    percentage = (
        correct_answer_count
        / question_count
        * 100
        if question_count
        else 0
    )

    duration_text = None

    if (
        attempt.started_at is not None
        and attempt.submitted_at is not None
    ):
        duration_seconds = max(
            int(
                (
                    attempt.submitted_at
                    - attempt.started_at
                ).total_seconds()
            ),
            0,
        )

        duration_minutes, seconds = divmod(
            duration_seconds,
            60,
        )

        hours, minutes = divmod(
            duration_minutes,
            60,
        )

        if hours:
            duration_text = _(
                "%(hours)s h %(minutes)s min "
                "%(seconds)s sec",
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            )
        elif minutes:
            duration_text = _(
                "%(minutes)s min %(seconds)s sec",
                minutes=minutes,
                seconds=seconds,
            )
        else:
            duration_text = _(
                "%(seconds)s sec",
                seconds=seconds,
            )

    return render_template(
        "admin/attempt_result_detail.html",
        attempt=attempt,
        generated_test=generated_test,
        question_results=question_results,
        question_count=question_count,
        correct_answer_count=correct_answer_count,
        percentage=percentage,
        duration_text=duration_text,
    )

@admin_bp.get("/questions")
def questions():
    page = request.args.get(
        "page",
        default=1,
        type=int,
    )

    search_text = request.args.get(
        "q",
        default="",
        type=str,
    ).strip()

    grade_id = request.args.get(
        "grade_id",
        default=0,
        type=int,
    )

    topic_id = request.args.get(
        "topic_id",
        default=0,
        type=int,
    )

    source_year_id = request.args.get(
        "source_year_id",
        default=0,
        type=int,
    )

    status = request.args.get(
        "status",
        default="all",
        type=str,
    )

    question_query = Question.query

    if search_text:
        question_query = question_query.filter(
            Question.question_text.ilike(
                f"%{search_text}%"
            )
        )

    if grade_id:
        question_query = question_query.filter(
            Question.grades.any(
                Grade.id == grade_id
            )
        )

    if topic_id:
        question_query = question_query.filter(
            Question.topics.any(
                Topic.id == topic_id
            )
        )

    if source_year_id:
        question_query = question_query.filter(
            Question.source_year_id
            == source_year_id
        )

    if status == "active":
        question_query = question_query.filter(
            Question.is_active.is_(True)
        )

    elif status == "inactive":
        question_query = question_query.filter(
            Question.is_active.is_(False)
        )

    pagination = (
        question_query
        .order_by(
            Question.source_year_id.desc(),
            Question.original_position.asc(),
        )
        .paginate(
            page=page,
            per_page=50,
            error_out=False,
        )
    )

    grades = (
        Grade.query
        .order_by(
            Grade.grade_number.asc()
        )
        .all()
    )

    topics = (
        Topic.query
        .order_by(
            Topic.name.asc()
        )
        .all()
    )

    source_years = (
        SourceYear.query
        .order_by(
            SourceYear.year_number.desc()
        )
        .all()
    )

    return render_template(
        "admin/questions.html",
        questions=pagination.items,
        pagination=pagination,
        search_text=search_text,
        grades=grades,
        topics=topics,
        source_years=source_years,
        selected_grade_id=grade_id,
        selected_topic_id=topic_id,
        selected_source_year_id=source_year_id,
        selected_status=status,
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
                _("Érvényes forrásévet kell választani.")
            )

        if (
            original_position is None
            or not 1 <= original_position <= 25
        ):
            errors.append(
                _("A feladat sorszáma 1 és 25 közötti lehet.")
            )

        if (
            difficulty is None
            or not 1 <= difficulty <= 25
        ):
            errors.append(
                _("A nehézség 1 és 25 közötti lehet.")
            )

        if not question_text:
            errors.append(
                _("A feladat szövege kötelező.")
            )

        if not selected_grade_ids:
            errors.append(
                _("Legalább egy évfolyamot ki kell választani.")
            )

        if not selected_topic_ids:
            errors.append(
                _("Legalább egy témakört ki kell választani.")
            )

        if any(
            not answer_text
            for answer_text in answer_texts
        ):
            errors.append(
                _("Mind az öt válaszlehetőséget ki kell tölteni.")
            )

        if correct_answer not in range(1, 6):
            errors.append(
                _("Ki kell választani a helyes választ.")
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
                _("Az évfolyamválasztás érvénytelen.")
            )

        if len(selected_topics) != len(
            set(selected_topic_ids)
        ):
            errors.append(
                _("A témakörválasztás érvénytelen.")
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
                    _(
                    "A feladatot és az öt "
                    "válaszlehetőséget elmentettük."
                )
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
    "/competitors/new",
    methods=["GET", "POST"],
)
def competitor_create():
    grades = (
        Grade.query
        .order_by(
            Grade.grade_number.asc()
        )
        .all()
    )

    if request.method == "POST":
        full_name = request.form.get(
            "full_name",
            "",
        ).strip()

        username = request.form.get(
            "username",
            "",
        ).strip()

        grade_id = request.form.get(
            "grade_id",
            type=int,
        )

        preferred_language = request.form.get(
            "preferred_language",
            "hu",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        password_confirm = request.form.get(
            "password_confirm",
            "",
        )

        has_error = False

        if not full_name:
            flash(
                _("A teljes név megadása kötelező."),
                "error",
            )
            has_error = True

        if not username:
            flash(
                _("A felhasználónév megadása kötelező."),
                "error",
            )
            has_error = True

        if len(username) > 80:
            flash(
                _("A felhasználónév legfeljebb 80 karakter lehet."),
                "error",
            )
            has_error = True

        existing_competitor = (
            Competitor.query
            .filter(
                Competitor.username.ilike(username)
            )
            .first()
        )

        if existing_competitor:
            flash(
                _("Ez a felhasználónév már foglalt."),
                "error",
            )
            has_error = True

        grade = db.session.get(
            Grade,
            grade_id,
        )

        if not grade:
            flash(
                _("Érvényes évfolyam kiválasztása kötelező."),
                "error",
            )
            has_error = True

        if preferred_language not in {"hu", "en"}:
            flash(
                _("Érvényes nyelvet kell választani."),
                "error",
            )
            has_error = True

        if len(password) < 6:
            flash(
                _("A jelszónak legalább 6 karakteresnek kell lennie."),
                "error",
            )
            has_error = True

        if password != password_confirm:
            flash(
                _("A két jelszó nem egyezik."),
                "error",
            )
            has_error = True

        if not has_error:
            competitor = Competitor(
                full_name=full_name,
                username=username,
                grade_id=grade.id,
                preferred_language=preferred_language,
                is_active=True,
            )

            competitor.set_password(password)

            db.session.add(competitor)
            db.session.commit()

            flash(
                _("A versenyző sikeresen létrejött."),
                "success",
            )

            return redirect(
                url_for("admin.competitors")
            )

    return render_template(
        "admin/competitor_form.html",
        grades=grades,
    )

@admin_bp.route(
    "/competitors/<int:competitor_id>/edit",
    methods=["GET", "POST"],
)
def competitor_edit(competitor_id):
    competitor = db.get_or_404(
        Competitor,
        competitor_id,
    )

    grades = (
        Grade.query
        .order_by(
            Grade.grade_number.asc()
        )
        .all()
    )

    if request.method == "POST":
        full_name = request.form.get(
            "full_name",
            "",
        ).strip()

        username = request.form.get(
            "username",
            "",
        ).strip()

        grade_id = request.form.get(
            "grade_id",
            type=int,
        )

        preferred_language = request.form.get(
            "preferred_language",
            competitor.preferred_language or "hu",
        ).strip().lower()

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        password = request.form.get(
            "password",
            "",
        )

        password_confirm = request.form.get(
            "password_confirm",
            "",
        )

        has_error = False

        if not full_name:
            flash(
                _("A teljes név megadása kötelező."),
                "error",
            )
            has_error = True

        if len(full_name) > 200:
            flash(
                _("A teljes név legfeljebb 200 karakter lehet."),
                "error",
            )
            has_error = True

        if not username:
            flash(
                _("A felhasználónév megadása kötelező."),
                "error",
            )
            has_error = True

        if len(username) > 80:
            flash(
                _("A felhasználónév legfeljebb 80 karakter lehet."),
                "error",
            )
            has_error = True

        existing_competitor = (
            Competitor.query
            .filter(
                Competitor.username.ilike(username),
                Competitor.id != competitor.id,
            )
            .first()
        )

        if existing_competitor:
            flash(
                _("Ez a felhasználónév már foglalt."),
                "error",
            )
            has_error = True

        grade = db.session.get(
            Grade,
            grade_id,
        )

        if not grade:
            flash(
                _("Érvényes évfolyam kiválasztása kötelező."),
                "error",
            )
            has_error = True

        if preferred_language not in {"hu", "en"}:
            flash(
                _("Érvényes nyelvet kell választani."),
                "error",
            )
            has_error = True

        if password:
            if len(password) < 6:
                flash(
                    _("Az új jelszónak legalább 6 karakteresnek kell lennie."),
                    "error",
                )
                has_error = True

            if password != password_confirm:
                flash(
                    _("A két új jelszó nem egyezik."),
                    "error",
                )
                has_error = True

        if not has_error:
            competitor.full_name = full_name
            competitor.username = username
            competitor.grade_id = grade.id
            competitor.preferred_language = preferred_language
            competitor.is_active = is_active

            if password:
                competitor.set_password(password)

            db.session.commit()

            flash(
                _("A versenyző adatai sikeresen módosultak."),
                "success",
            )

            return redirect(
                url_for("admin.competitors")
            )

    return render_template(
        "admin/competitor_edit.html",
        competitor=competitor,
        grades=grades,
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
                _("Érvényes forrásévet kell választani.")
            )

        if (
            original_position is None
            or not 1 <= original_position <= 25
        ):
            errors.append(
                _("A feladat sorszáma 1 és 25 közötti lehet.")
            )

        if (
            difficulty is None
            or not 1 <= difficulty <= 25
        ):
            errors.append(
                _("A nehézség 1 és 25 közötti lehet.")
            )

        if not question_text:
            errors.append(
                _("A feladat szövege kötelező.")
            )

        if not posted_grade_ids:
            errors.append(
                _("Legalább egy évfolyamot ki kell választani.")
            )

        if not posted_topic_ids:
            errors.append(
                _("Legalább egy témakört ki kell választani.")
            )

        if any(
            not answer_text
            for answer_text in answer_texts
        ):
            errors.append(
                _("Mind az öt válaszlehetőséget ki kell tölteni.")
            )

        if correct_answer not in range(1, 6):
            errors.append(
                _("Ki kell választani a helyes választ.")
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
                _("Az évfolyamválasztás érvénytelen.")
            )

        if len(selected_topics) != len(
            set(posted_topic_ids)
        ):
            errors.append(
                _("A témakörválasztás érvénytelen.")
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

            # Important: this is intentionally outside the loop.
            db.session.commit()

            flash(
                _("A feladat módosításait elmentettük."),
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

@admin_bp.route(
    "/questions/import",
    methods=["GET", "POST"],
)
def question_import():
    preview_rows = []
    import_errors = []

    if request.method == "POST":
        action = request.form.get(
            "action",
            "preview",
        )

        uploaded_file = request.files.get(
            "csv_file"
        )

        if (
            uploaded_file is None
            or not uploaded_file.filename
        ):
            flash(
                _("Nem választottál ki CSV-fájlt."),
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=import_errors,
            )

        if not uploaded_file.filename.lower().endswith(
            ".csv"
        ):
            flash(
                _("Csak CSV-fájl tölthető fel."),
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=import_errors,
            )

        try:
            file_content = uploaded_file.read().decode(
                "utf-8-sig"
            )

        except UnicodeDecodeError:
            flash(
                (
                    _(
                    "A CSV nem olvasható "
                    "UTF-8 kódolással."
                )
                ),
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=import_errors,
            )

        reader = csv.DictReader(
            io.StringIO(file_content),
            delimiter=";",
        )

        actual_fieldnames = reader.fieldnames or []

        if actual_fieldnames != CSV_FIELDNAMES:
            flash(
                _("A CSV fejlécének formátuma hibás."),
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=[
                    {
                        "line": 1,
                        "messages": [
                            (
                                _(
                                "Elvárt fejléc: %(header)s",
                                header=";".join(
                                    CSV_FIELDNAMES
                                ),
                            )
                            )
                        ],
                    }
                ],
            )

        grade_by_number = {
            grade.grade_number: grade
            for grade in Grade.query.all()
        }

        topic_by_name = {
            topic.name.casefold(): topic
            for topic in Topic.query.all()
        }

        source_year_by_number = {
            source_year.year_number: source_year
            for source_year
            in SourceYear.query.all()
        }

        existing_question_keys = {
            (
                question.source_year.year_number,
                question.original_position,
                question.question_text.strip().casefold(),
            ): question.id
            for question in Question.query.all()
        }

        csv_question_keys = set()

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            row_errors = []

            normalized_row = {
                key: (
                    value.strip()
                    if value is not None
                    else ""
                )
                for key, value in row.items()
            }

            try:
                source_year_number = int(
                    normalized_row["forrasev"]
                )
            except ValueError:
                source_year_number = None
                row_errors.append(
                    _("A forrásév nem érvényes szám.")
                )

            try:
                original_position = int(
                    normalized_row["sorszam"]
                )
            except ValueError:
                original_position = None
                row_errors.append(
                    _("A sorszám nem érvényes szám.")
                )

            try:
                difficulty = int(
                    normalized_row["nehezseg"]
                )
            except ValueError:
                difficulty = None
                row_errors.append(
                    _("A nehézség nem érvényes szám.")
                )

            try:
                correct_answer = int(
                    normalized_row["helyes"]
                )
            except ValueError:
                correct_answer = None
                row_errors.append(
                    (
                        _(
                        "A helyes válasz "
                        "nem érvényes szám."
                    )
                    )
                )

            if (
                source_year_number is not None
                and source_year_number
                not in source_year_by_number
            ):
                row_errors.append(
                    (
                        _(
                        "A forrásév nincs rögzítve: "
                        "%(year)s.",
                        year=source_year_number,
                    )
                    )
                )

            if (
                original_position is not None
                and not 1 <= original_position <= 25
            ):
                row_errors.append(
                    (
                        _(
                        "A sorszám 1 és 25 "
                        "közötti lehet."
                    )
                    )
                )

            if (
                difficulty is not None
                and not 1 <= difficulty <= 25
            ):
                row_errors.append(
                    (
                        _(
                        "A nehézség 1 és 25 "
                        "közötti lehet."
                    )
                    )
                )

            if (
                correct_answer is not None
                and correct_answer
                not in range(1, 6)
            ):
                row_errors.append(
                    (
                        _(
                        "A helyes válasz 1 és 5 "
                        "közötti lehet."
                    )
                    )
                )

            grade_numbers = []

            for grade_value in normalized_row[
                "evfolyamok"
            ].split("|"):
                grade_value = grade_value.strip()

                if not grade_value:
                    continue

                try:
                    grade_number = int(
                        grade_value
                    )

                except ValueError:
                    row_errors.append(
                        (
                            _(
                            "Érvénytelen évfolyam: "
                            "%(grade)s.",
                            grade=grade_value,
                        )
                        )
                    )
                    continue

                if grade_number not in grade_by_number:
                    row_errors.append(
                        (
                            _(
                            "Nem létező évfolyam: "
                            "%(grade)s.",
                            grade=grade_number,
                        )
                        )
                    )
                else:
                    grade_numbers.append(
                        grade_number
                    )

            if not grade_numbers:
                row_errors.append(
                    (
                        _(
                        "Legalább egy évfolyam "
                        "szükséges."
                    )
                    )
                )

            topic_names = []

            for topic_value in normalized_row[
                "temakorok"
            ].split("|"):
                topic_value = topic_value.strip()

                if not topic_value:
                    continue

                topic_key = topic_value.casefold()

                if topic_key not in topic_by_name:
                    row_errors.append(
                        (
                            _(
                            "Nem létező témakör: "
                            "%(topic)s.",
                            topic=topic_value,
                        )
                        )
                    )
                else:
                    topic_names.append(
                        topic_by_name[
                            topic_key
                        ].name
                    )

            if not topic_names:
                row_errors.append(
                    (
                        _(
                        "Legalább egy témakör "
                        "szükséges."
                    )
                    )
                )

            if not normalized_row["feladat"]:
                row_errors.append(
                    _("A feladat szövege kötelező.")
                )

            if (
                source_year_number is not None
                and original_position is not None
                and normalized_row["feladat"]
            ):
                question_key = (
                    source_year_number,
                    original_position,
                    normalized_row[
                        "feladat"
                    ].strip().casefold(),
                )

                existing_question_id = (
                    existing_question_keys.get(
                        question_key
                    )
                )

                if existing_question_id is not None:
                    row_errors.append(
                        (
                            _(
                            "A feladat valószínűleg már "
                            "létezik az adatbázisban. "
                            "Feladat ID: %(question_id)s.",
                            question_id=existing_question_id,
                        )
                        )
                    )

                if question_key in csv_question_keys:
                    row_errors.append(
                        (
                            _(
                            "Ugyanez a feladat már korábban "
                            "szerepelt ebben a CSV-fájlban."
                        )
                        )
                    )
                else:
                    csv_question_keys.add(
                        question_key
                    )

            answer_texts = [
                normalized_row[
                    f"valasz{position}"
                ]
                for position in range(1, 6)
            ]

            if any(
                not answer_text
                for answer_text in answer_texts
            ):
                row_errors.append(
                    (
                        _(
                        "Mind az öt "
                        "válaszlehetőséget "
                        "ki kell tölteni."
                    )
                    )
                )

            is_active = parse_boolean(
                normalized_row["aktiv"]
            )

            if is_active is None:
                row_errors.append(
                    (
                        _(
                        "Az aktív mező értéke "
                        "legyen igen vagy nem."
                    )
                    )
                )

            preview_row = {
                "line": line_number,
                "source_year": source_year_number,
                "source_year_object": (
                    source_year_by_number.get(
                        source_year_number
                    )
                ),
                "original_position": (
                    original_position
                ),
                "difficulty": difficulty,
                "grades": grade_numbers,
                "grade_objects": [
                    grade_by_number[
                        grade_number
                    ]
                    for grade_number
                    in grade_numbers
                    if grade_number
                    in grade_by_number
                ],
                "topics": topic_names,
                "topic_objects": [
                    topic_by_name[
                        topic_name.casefold()
                    ]
                    for topic_name
                    in topic_names
                    if topic_name.casefold()
                    in topic_by_name
                ],
                "question_text": normalized_row[
                    "feladat"
                ],
                "answer_texts": answer_texts,
                "correct_answer": correct_answer,
                "explanation": normalized_row[
                    "magyarazat"
                ],
                "is_active": is_active,
                "errors": row_errors,
            }

            preview_rows.append(
                preview_row
            )

            if row_errors:
                import_errors.append(
                    {
                        "line": line_number,
                        "messages": row_errors,
                    }
                )

        # Important: this is intentionally outside the for loop.
        if not preview_rows:
            flash(
                _("A CSV nem tartalmaz adatsort."),
                "error",
            )

        elif import_errors:
            flash(
                (
                    _(
                    "%(count)s hibás CSV-sor található. "
                    "Az import nem történt meg.",
                    count=len(import_errors),
                )
                ),
                "error",
            )

        elif action == "import":
            try:
                imported_questions = []

                for row in preview_rows:
                    question = Question(
                        source_year=row[
                            "source_year_object"
                        ],
                        original_position=row[
                            "original_position"
                        ],
                        difficulty=row[
                            "difficulty"
                        ],
                        question_text=row[
                            "question_text"
                        ],
                        explanation=(
                            row["explanation"]
                            or None
                        ),
                        is_active=row[
                            "is_active"
                        ],
                    )

                    question.grades = row[
                        "grade_objects"
                    ]

                    question.topics = row[
                        "topic_objects"
                    ]

                    for (
                        position,
                        answer_text,
                    ) in enumerate(
                        row["answer_texts"],
                        start=1,
                    ):
                        question.answer_options.append(
                            AnswerOption(
                                original_position=(
                                    position
                                ),
                                answer_text=(
                                    answer_text
                                ),
                                is_correct=(
                                    position
                                    == row[
                                        "correct_answer"
                                    ]
                                ),
                            )
                        )

                    db.session.add(
                        question
                    )

                    imported_questions.append(
                        question
                    )

                db.session.flush()

                imported_summary = [
                    {
                        "line": row["line"],
                        "question_id": (
                            question.id
                        ),
                        "image_filename": (
                            question.image_filename
                        ),
                    }
                    for row, question in zip(
                        preview_rows,
                        imported_questions,
                    )
                ]

                db.session.commit()

            except Exception:
                db.session.rollback()

                current_app.logger.exception(
                    (
                        "CSV import failed."
                    )
                )

                flash(
                    (
                        _(
                        "Az importálás közben "
                        "hiba történt. Egyetlen "
                        "rekordot sem mentettünk el."
                    )
                    ),
                    "error",
                )

            else:
                return render_template(
                    (
                        "admin/"
                        "question_import_result.html"
                    ),
                    imported_summary=(
                        imported_summary
                    ),
                )

        else:
            flash(
                (
                    _(
                    "%(count)s sor ellenőrzése sikeres. "
                    "Az adatok még nem kerültek "
                    "az adatbázisba.",
                    count=len(preview_rows),
                )
                ),
                "success",
            )

    return render_template(
        "admin/question_import.html",
        preview_rows=preview_rows,
        import_errors=import_errors,
    )

@admin_bp.post(
    "/questions/<int:question_id>/toggle-active"
)
def question_toggle_active(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    question.is_active = not question.is_active

    db.session.commit()

    if question.is_active:
        message = _("A feladatot aktiváltuk.")
    else:
        message = _("A feladatot inaktiváltuk.")

    flash(
        message,
        "success",
    )

    return redirect(
        url_for(
            "admin.question_detail",
            question_id=question.id,
        )
    )

@admin_bp.get("/competitors")
def competitors():
    page = request.args.get(
        "page",
        default=1,
        type=int,
    )

    search_text = request.args.get(
        "q",
        default="",
        type=str,
    ).strip()

    competitor_query = Competitor.query

    if search_text:
        competitor_query = competitor_query.filter(
            db.or_(
                Competitor.username.ilike(
                    f"%{search_text}%"
                ),
                Competitor.full_name.ilike(
                    f"%{search_text}%"
                ),
            )
        )

    pagination = (
        competitor_query
        .order_by(
            Competitor.full_name.asc(),
            Competitor.id.asc(),
        )
        .paginate(
            page=page,
            per_page=50,
            error_out=False,
        )
    )

    return render_template(
        "admin/competitors.html",
        competitors=pagination.items,
        pagination=pagination,
        search_text=search_text,
    )
