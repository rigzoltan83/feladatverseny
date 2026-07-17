import random
from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from app.extensions import db
from app.models import (
    AnswerOption,
    GeneratedTest,
    GeneratedTestAnswer,
    GeneratedTestQuestion,
    Grade,
    Question,
    TestTemplate,
    Topic,
)


generated_test_bp = Blueprint(
    "admin_generated_tests",
    __name__,
    url_prefix="/admin/generated-tests",
)


def get_candidate_questions(
    template: TestTemplate,
) -> list[Question]:
    grade_ids = [
        grade.id
        for grade in template.grades
    ]

    topic_ids = [
        topic.id
        for topic in template.topics
    ]

    if not grade_ids or not topic_ids:
        return []

    candidates = (
        Question.query
        .filter(
            Question.is_active.is_(True),
            Question.grades.any(
                Grade.id.in_(grade_ids)
            ),
            Question.topics.any(
                Topic.id.in_(topic_ids)
            ),
        )
        .order_by(
            Question.difficulty,
            Question.id,
        )
        .all()
    )

    valid_candidates = []

    for question in candidates:
        answers = list(
            question.answer_options
        )

        correct_count = sum(
            1
            for answer in answers
            if answer.is_correct
        )

        if (
            len(answers) == 5
            and correct_count == 1
        ):
            valid_candidates.append(
                question
            )

    return valid_candidates


@generated_test_bp.get("/")
def generated_test_list():
    generated_tests = (
        GeneratedTest.query
        .order_by(
            GeneratedTest.created_at.desc(),
            GeneratedTest.id.desc(),
        )
        .all()
    )

    return render_template(
        "admin/generated_tests.html",
        generated_tests=generated_tests,
    )


@generated_test_bp.post(
    "/generate/<int:template_id>"
)
def generate_test(template_id: int):
    template = db.get_or_404(
        TestTemplate,
        template_id,
    )

    if not template.is_active:
        flash(
            (
                "Inaktív tesztsablonból "
                "nem generálható feladatsor."
            ),
            "error",
        )

        return redirect(
            url_for(
                "admin_templates.template_detail",
                template_id=template.id,
            )
        )

    candidates = get_candidate_questions(
        template
    )

    if len(candidates) < template.question_count:
        flash(
            (
                "Nincs elegendő megfelelő feladat. "
                f"Elérhető: {len(candidates)}, "
                f"szükséges: {template.question_count}."
            ),
            "error",
        )

        return redirect(
            url_for(
                "admin_templates.template_detail",
                template_id=template.id,
            )
        )

    if template.shuffle_questions:
        selected_questions = random.sample(
            candidates,
            template.question_count,
        )
    else:
        selected_questions = candidates[
            :template.question_count
        ]

    generated_name = (
        f"{template.name} – "
        f"{datetime.now():%Y-%m-%d %H:%M:%S}"
    )

    try:
        generated_test = GeneratedTest(
            test_template=template,
            name=generated_name,
            status="draft",
        )

        db.session.add(
            generated_test
        )

        db.session.flush()

        for question_position, question in enumerate(
            selected_questions,
            start=1,
        ):
            generated_question = (
                GeneratedTestQuestion(
                    generated_test=generated_test,
                    question=question,
                    display_position=(
                        question_position
                    ),
                )
            )

            db.session.add(
                generated_question
            )

            db.session.flush()

            answers = sorted(
                question.answer_options,
                key=lambda answer: (
                    answer.original_position
                ),
            )

            if template.shuffle_answers:
                random.shuffle(answers)

            for answer_position, answer in enumerate(
                answers,
                start=1,
            ):
                db.session.add(
                    GeneratedTestAnswer(
                        generated_test_question=(
                            generated_question
                        ),
                        answer_option=answer,
                        display_position=(
                            answer_position
                        ),
                    )
                )

        db.session.commit()

    except Exception:
        db.session.rollback()

        raise

    flash(
        (
            f"A feladatsor elkészült "
            f"{template.question_count} feladattal."
        ),
        "success",
    )

    return redirect(
        url_for(
            "admin_generated_tests.generated_test_detail",
            generated_test_id=generated_test.id,
        )
    )


@generated_test_bp.get(
    "/<int:generated_test_id>"
)
def generated_test_detail(
    generated_test_id: int,
):
    generated_test = db.get_or_404(
        GeneratedTest,
        generated_test_id,
    )

    return render_template(
        "admin/generated_test_detail.html",
        generated_test=generated_test,
    )

@generated_test_bp.post(
    "/<int:generated_test_id>/activate"
)
def generated_test_activate(
    generated_test_id: int,
):
    generated_test = db.get_or_404(
        GeneratedTest,
        generated_test_id,
    )

    if generated_test.status == "closed":
        flash(
            (
                "Lezárt feladatsor nem "
                "aktiválható újra."
            ),
            "error",
        )

    elif generated_test.status == "active":
        flash(
            "A feladatsor már aktív.",
            "error",
        )

    else:
        generated_test.status = "active"
        db.session.commit()

        flash(
            "A feladatsort aktiváltuk.",
            "success",
        )

    return redirect(
        url_for(
            "admin_generated_tests.generated_test_detail",
            generated_test_id=generated_test.id,
        )
    )


@generated_test_bp.post(
    "/<int:generated_test_id>/close"
)
def generated_test_close(
    generated_test_id: int,
):
    generated_test = db.get_or_404(
        GeneratedTest,
        generated_test_id,
    )

    if generated_test.status == "closed":
        flash(
            "A feladatsor már le van zárva.",
            "error",
        )

    else:
        generated_test.status = "closed"
        db.session.commit()

        flash(
            "A feladatsort lezártuk.",
            "success",
        )

    return redirect(
        url_for(
            "admin_generated_tests.generated_test_detail",
            generated_test_id=generated_test.id,
        )
    )


@generated_test_bp.post(
    "/<int:generated_test_id>/return-to-draft"
)
def generated_test_return_to_draft(
    generated_test_id: int,
):
    generated_test = db.get_or_404(
        GeneratedTest,
        generated_test_id,
    )

    if generated_test.status == "closed":
        flash(
            (
                "Lezárt feladatsor nem "
                "állítható vissza piszkozatba."
            ),
            "error",
        )

    elif generated_test.status == "draft":
        flash(
            "A feladatsor már piszkozat.",
            "error",
        )

    else:
        generated_test.status = "draft"
        db.session.commit()

        flash(
            (
                "A feladatsort visszaállítottuk "
                "piszkozat állapotba."
            ),
            "success",
        )

    return redirect(
        url_for(
            "admin_generated_tests.generated_test_detail",
            generated_test_id=generated_test.id,
        )
    )


