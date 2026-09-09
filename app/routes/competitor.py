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

from flask_babel import gettext as _

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


@competitor_bp.get("/nyelv/<language>")
def set_language(language):
    language = language.strip().lower()

    if language not in {"hu", "en"}:
        language = "hu"

    session["language"] = language

    competitor_id = session.get(
        "competitor_id"
    )

    if competitor_id:
        competitor = db.session.get(
            Competitor,
            competitor_id,
        )

        if competitor is not None:
            competitor.preferred_language = (
                language
            )
            db.session.commit()

    response = make_response(
        redirect(
            request.referrer
            or url_for("competitor.login")
        )
    )

    response.set_cookie(
        "feladatverseny_language",
        language,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="Lax",
        path=request.script_root or "/",
    )

    return response


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

        selected_language = session.get(
            "language",
            default_language,
        )

        if selected_language not in {"hu", "en"}:
            selected_language = "hu"

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
                _("Sikeres bejelentkezés."),
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
            _(
                "Hibás felhasználónév vagy jelszó."
            ),
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
        _("Sikeresen kijelentkeztél."),
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
            _(
                "Az oldal megtekintéséhez "
                "jelentkezz be."
            ),
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
            _(
                "A felhasználói fiók "
                "nem érhető el."
            ),
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

        selected_answers = {}

        for competitor_answer in attempt.answers:
            selected_answers.setdefault(
                competitor_answer
                .generated_test_question_id,
                set(),
            ).add(
                competitor_answer
                .generated_test_answer_id
            )

        score = 0

        for generated_question in (
            attempt.generated_test.generated_questions
        ):
            correct_answer_ids = {
                generated_answer.id
                for generated_answer
                in generated_question.generated_answers
                if (
                    generated_answer
                    .answer_option
                    .is_correct
                )
            }

            selected_answer_ids = (
                selected_answers.get(
                    generated_question.id,
                    set(),
                )
            )

            if (
                correct_answer_ids
                and selected_answer_ids
                == correct_answer_ids
            ):
                score += 1

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

                other_selected_answers = {}

                for competitor_answer in (
                    other_attempt.answers
                ):
                    other_selected_answers.setdefault(
                        competitor_answer
                        .generated_test_question_id,
                        set(),
                    ).add(
                        competitor_answer
                        .generated_test_answer_id
                    )

                other_score = 0

                for generated_question in (
                    other_attempt
                    .generated_test
                    .generated_questions
                ):
                    correct_answer_ids = {
                        generated_answer.id
                        for generated_answer
                        in (
                            generated_question
                            .generated_answers
                        )
                        if (
                            generated_answer
                            .answer_option
                            .is_correct
                        )
                    }

                    selected_answer_ids = (
                        other_selected_answers.get(
                            generated_question.id,
                            set(),
                        )
                    )

                    if (
                        correct_answer_ids
                        and selected_answer_ids
                        == correct_answer_ids
                    ):
                        other_score += 1

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
            _(
                "A feladatsor megtekintéséhez "
                "jelentkezz be."
            ),
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
            _(
                "A felhasználói fiók "
                "nem érhető el."
            ),
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
            _(
                "Ez a feladatsor számodra "
                "nem érhető el."
            ),
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
                _(
                    "A forduló lezárult, ezért "
                    "a válaszok már nem "
                    "módosíthatók."
                ),
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
                _(
                    "A feladatsor már le van zárva, "
                    "ezért nem módosítható."
                ),
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

        for generated_question in test_questions:
            field_name = (
                f"question_{generated_question.id}"
            )

            valid_answer_ids = {
                answer.id
                for answer
                in generated_question.generated_answers
            }

            selected_answer_ids = set(
                request.form.getlist(
                    field_name,
                    type=int,
                )
            )

            selected_answer_ids.intersection_update(
                valid_answer_ids
            )

            existing_answers = (
                CompetitorAnswer.query
                .filter_by(
                    attempt_id=attempt.id,
                    generated_test_question_id=(
                        generated_question.id
                    ),
                )
                .all()
            )

            existing_by_answer_id = {
                competitor_answer.generated_test_answer_id:
                    competitor_answer
                for competitor_answer
                in existing_answers
            }

            for (
                generated_answer_id,
                competitor_answer,
            ) in existing_by_answer_id.items():
                if (
                    generated_answer_id
                    not in selected_answer_ids
                ):
                    db.session.delete(
                        competitor_answer
                    )

            for generated_answer_id in (
                selected_answer_ids
                - set(existing_by_answer_id)
            ):
                db.session.add(
                    CompetitorAnswer(
                        attempt_id=attempt.id,
                        generated_test_question_id=(
                            generated_question.id
                        ),
                        generated_test_answer_id=(
                            generated_answer_id
                        ),
                    )
                )

        if action == "submit":
            attempt.status = "submitted"
            attempt.submitted_at = db.func.now()

            db.session.commit()

            flash(
                _(
                    "A feladatsor végleges "
                    "beküldése sikerült."
                ),
                "success",
            )
        else:
            db.session.commit()

            flash(
                _("A válaszok mentése sikerült."),
                "success",
            )

        return redirect(
            url_for(
                "competitor.test_view",
                test_id=generated_test.id,
            )
        )

    saved_answers = {}

    for answer in attempt.answers:
        saved_answers.setdefault(
            answer.generated_test_question_id,
            set(),
        ).add(
            answer.generated_test_answer_id
        )

    correct_answer_count = 0
    total_question_count = len(
        test_questions
    )

    if results_visible:
        for generated_question in test_questions:
            selected_answer_ids = saved_answers.get(
                generated_question.id,
                set(),
            )

            correct_answer_ids = {
                generated_answer.id
                for generated_answer
                in generated_question.generated_answers
                if (
                    generated_answer
                    .answer_option
                    .is_correct
                )
            }

            if (
                correct_answer_ids
                and selected_answer_ids
                == correct_answer_ids
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

