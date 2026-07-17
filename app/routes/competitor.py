from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
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

    return render_template(
        "competitor/dashboard.html",
        competitor=competitor,
        active_tests=active_tests,
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

    is_allowed = (
        generated_test.status == "active"
        and any(
            grade.id == competitor.grade_id
            for grade in generated_test.test_template.grades
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

    test_questions = generated_test.generated_questions

    attempt = (
        CompetitorAttempt.query
        .filter_by(
            competitor_id=competitor.id,
            generated_test_id=generated_test.id,
        )
        .first()
    )

    if attempt is None:
        attempt = CompetitorAttempt(
            competitor_id=competitor.id,
            generated_test_id=generated_test.id,
            status="in_progress",
        )

        db.session.add(attempt)
        db.session.commit()

    if request.method == "POST":
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

    return render_template(
        "competitor/test_view.html",
        competitor=competitor,
        generated_test=generated_test,
        test_questions=test_questions,
        attempt=attempt,
        saved_answers=saved_answers,
    )

