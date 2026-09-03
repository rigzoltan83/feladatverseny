from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    make_response,
)

from app.models import (
    Competitor,
    CompetitorAnswer,
    CompetitorAttempt,
    GeneratedTest,
    GeneratedTestAnswer,
    Grade,
    TestTemplate,
)

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
        if session.get("is_admin"):
            return redirect(
                url_for("admin.index")
            )

        return redirect(
            url_for("competitor.dashboard")
        )

    default_language = request.cookies.get(
        "feladatverseny_language",
        "hu",
    ).strip().lower()

    if default_language not in {"hu", "en"}:
        default_language = "hu"

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        selected_language = request.form.get(
            "language",
            default_language,
        ).strip().lower()

        if selected_language not in {"hu", "en"}:
            selected_language = "hu"

        default_language = selected_language

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
            competitor.preferred_language = (
                selected_language
            )

            db.session.commit()

            session.clear()

            session["competitor_id"] = competitor.id
            session["competitor_name"] = (
                competitor.full_name
            )
            session["is_admin"] = competitor.is_admin
            session["language"] = selected_language

            flash(
                "Sikeres bejelentkezés.",
                "success",
            )

            if competitor.is_admin:
                response = make_response(
                    redirect(
                        url_for("admin.index")
                    )
                )
            else:
                response = make_response(
                    redirect(
                        url_for(
                            "competitor.dashboard"
                        )
                    )
                )

            response.set_cookie(
                "feladatverseny_language",
                selected_language,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax",
                path=request.script_root or "/",
            )

            return response

        flash(
            "Hibás felhasználónév vagy jelszó.",
            "error",
        )

    return render_template(
        "competitor/login.html",
        default_language=default_language,
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

    competitor = db.session.get(
        Competitor,
        competitor_id,
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

    active_tests = (
        GeneratedTest.query
        .join(GeneratedTest.test_template)
        .filter(
            GeneratedTest.status == "active",
            GeneratedTest.test_template.has(
                TestTemplate.grades.any(
                    Grade.id == competitor.grade_id
                )
            ),
        )
        .order_by(
            GeneratedTest.created_at.desc(),
            GeneratedTest.id.desc(),
        )
        .all()
    )

    closed_attempts = (
        CompetitorAttempt.query
        .join(CompetitorAttempt.generated_test)
        .filter(
            CompetitorAttempt.competitor_id
            == competitor.id,
            GeneratedTest.status == "closed",
        )
        .order_by(
            GeneratedTest.created_at.desc(),
            GeneratedTest.id.desc(),
        )
        .all()
    )

    result_rows = []

    for attempt in closed_attempts:
        question_count = len(
            attempt.generated_test.generated_questions
        )

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

        rank = None

        if attempt.status == "submitted":
            submitted_scores = []

            for other_attempt in (
                attempt.generated_test
                .competitor_attempts
                .all()
            ):
                if other_attempt.status != "submitted":
                    continue

                other_score = sum(
                    1
                    for competitor_answer
                    in other_attempt.answers
                    if (
                        competitor_answer
                        .generated_test_answer
                        .answer_option
                        .is_correct
                    )
                )

                submitted_scores.append(
                    {
                        "attempt_id":
                            other_attempt.id,
                        "score":
                            other_score,
                    }
                )

            submitted_scores.sort(
                key=lambda item: -item["score"]
            )

            current_rank = 0
            previous_score = None

            for row_number, score_row in enumerate(
                submitted_scores,
                start=1,
            ):
                if (
                    score_row["score"]
                    != previous_score
                ):
                    current_rank = row_number
                    previous_score = score_row["score"]

                if (
                    score_row["attempt_id"]
                    == attempt.id
                ):
                    rank = current_rank
                    break

        result_rows.append(
            {
                "attempt": attempt,
                "question_count": question_count,
                "score": score,
                "percentage": percentage,
                "rank": rank,
            }
        )

    return render_template(
        "competitor/dashboard.html",
        competitor=competitor,
        active_tests=active_tests,
        result_rows=result_rows,
    )

@competitor_bp.route(
    "/feladatsor/<int:test_id>",
    methods=["GET", "POST"],
)
def test_view(test_id):
    competitor_id = session.get(
        "competitor_id"
    )

    if not competitor_id:
        flash(
            "A feladatsor megtekintéséhez jelentkezz be.",
            "error",
        )

        return redirect(
            url_for("competitor.login")
        )

    competitor = db.session.get(
        Competitor,
        competitor_id,
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

    generated_test = db.get_or_404(
        GeneratedTest,
        test_id,
    )

    has_correct_grade = any(
        grade.id == competitor.grade_id
        for grade in generated_test.test_template.grades
    )

    attempt = (
        CompetitorAttempt.query
        .filter_by(
            competitor_id=competitor.id,
            generated_test_id=generated_test.id,
        )
        .first()
    )

    is_active = (
        generated_test.status == "active"
    )

    is_closed = (
        generated_test.status == "closed"
    )

    is_allowed = (
        has_correct_grade
        and (
            is_active
            or (
                is_closed
                and attempt is not None
            )
        )
    )

    if not is_allowed:
        flash(
            "Ez a feladatsor számodra nem érhető el.",
            "error",
        )

        return redirect(
            url_for("competitor.dashboard")
        )

    test_questions = (
        generated_test.generated_questions
    )

    if attempt is None:
        attempt = CompetitorAttempt(
            competitor_id=competitor.id,
            generated_test_id=generated_test.id,
            status="in_progress",
        )

        db.session.add(attempt)
        db.session.commit()

    results_visible = is_closed

    if request.method == "POST":

        if is_closed:
            flash(
                "A forduló lezárult, ezért a válaszok "
                "már nem módosíthatók.",
                "error",
            )

            return redirect(
                url_for(
                    "competitor.test_view",
                    test_id=generated_test.id,
                )
            )

        if attempt.status == "submitted":
            flash(
                "A feladatsor már le van zárva, ezért nem módosítható.",
                "error",
            )

            return redirect(
                url_for(
                    "competitor.test_view",
                    test_id=generated_test.id,
                )
            )

        action = request.form.get(
            "action",
            "save",
        )

        valid_question_ids = {
            question.id
            for question in test_questions
        }

        valid_answers = {
            answer.id: answer
            for question in test_questions
            for answer in question.generated_answers
        }

        for generated_question in test_questions:
            field_name = (
                f"question_{generated_question.id}"
            )

            selected_answer_id = request.form.get(
                field_name
            )

            if not selected_answer_id:
                continue

            try:
                selected_answer_id = int(
                    selected_answer_id
                )
            except ValueError:
                continue

            selected_answer = valid_answers.get(
                selected_answer_id
            )

            if (
                selected_answer is None
                or selected_answer.generated_test_question_id
                not in valid_question_ids
                or selected_answer.generated_test_question_id
                != generated_question.id
            ):
                continue

            competitor_answer = (
                CompetitorAnswer.query
                .filter_by(
                    attempt_id=attempt.id,
                    generated_test_question_id=(
                        generated_question.id
                    ),
                )
                .first()
            )

            if competitor_answer is None:
                competitor_answer = CompetitorAnswer(
                    attempt_id=attempt.id,
                    generated_test_question_id=(
                        generated_question.id
                    ),
                    generated_test_answer_id=(
                        selected_answer.id
                    ),
                )

                db.session.add(
                    competitor_answer
                )
            else:
                competitor_answer.generated_test_answer_id = (
                    selected_answer.id
                )

        if action == "submit":
            attempt.status = "submitted"
            attempt.submitted_at = db.func.now()

            db.session.commit()

            flash(
                "A feladatsor végleges beküldése sikerült.",
                "success",
            )
        else:
            db.session.commit()

            flash(
                "A válaszok mentése sikerült.",
                "success",
            )

        return redirect(
            url_for(
                "competitor.test_view",
                test_id=generated_test.id,
            )
        )

    saved_answers = {
        answer.generated_test_question_id:
            answer.generated_test_answer_id
        for answer in attempt.answers
    }

    correct_answer_count = 0
    total_question_count = len(
        test_questions
    )

    if results_visible:
        for generated_question in test_questions:
            selected_answer_id = saved_answers.get(
                generated_question.id
            )

            if selected_answer_id is None:
                continue

            selected_answer = next(
                (
                    answer
                    for answer
                    in generated_question.generated_answers
                    if answer.id == selected_answer_id
                ),
                None,
            )

            if (
                selected_answer is not None
                and selected_answer.answer_option.is_correct
            ):
                correct_answer_count += 1

    completion_seconds = None

    if (
        attempt.started_at is not None
        and attempt.submitted_at is not None
    ):
        completion_seconds = int(
            (
                attempt.submitted_at
                - attempt.started_at
            ).total_seconds()
        )

    completion_time = None

    if completion_seconds is not None:
        hours, remainder = divmod(
            completion_seconds,
            3600,
        )

        minutes, seconds = divmod(
            remainder,
            60,
        )

        completion_time = (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    return render_template(
        "competitor/test_view.html",
        competitor=competitor,
        generated_test=generated_test,
        test_questions=test_questions,
        attempt=attempt,
        saved_answers=saved_answers,
        completion_time=completion_time,
        results_visible=results_visible,
        correct_answer_count=correct_answer_count,
        total_question_count=total_question_count,
    )

