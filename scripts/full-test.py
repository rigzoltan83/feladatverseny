#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.models import (
    AnswerOption,
    Competitor,
    CompetitorAnswer,
    CompetitorAttempt,
    GeneratedTest,
    GeneratedTestAnswer,
    GeneratedTestQuestion,
    Grade,
    Question,
    SourceYear,
    TestTemplate,
    Topic,
)


ROOT = Path(__file__).resolve().parent.parent

passed = 0
failed = 0


def ok(name: str) -> None:
    global passed
    passed += 1
    print(f"[PASS] {name}")


def fail(name: str, detail: str = "") -> None:
    global failed
    failed += 1
    print(f"[FAIL] {name}")

    if detail:
        print(f"       {detail}")


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> None:
    if condition:
        ok(name)
    else:
        fail(name, detail)


def run_command(
    name: str,
    command: list[str],
) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode == 0:
        ok(name)
    else:
        fail(
            name,
            result.stdout.strip(),
        )


def score_question(
    generated_question,
    selected_answer_ids: set[int],
) -> bool:
    correct_answer_ids = {
        generated_answer.id
        for generated_answer
        in generated_question.generated_answers
        if generated_answer.answer_option.is_correct
    }

    return (
        bool(correct_answer_ids)
        and selected_answer_ids
        == correct_answer_ids
    )


def main() -> int:
    print("=" * 72)
    print("FELADATVERSENY FULL REGRESSION TEST")
    print("=" * 72)

    run_command(
        "Python source compile",
        [
            str(ROOT / "venv/bin/python"),
            "-m",
            "compileall",
            "-q",
            "app",
        ],
    )

    run_command(
        "Git diff whitespace check",
        [
            "git",
            "diff",
            "--check",
        ],
    )

    app = create_app()

    app.config.update(
        TESTING=True,
        PROPAGATE_EXCEPTIONS=True,
    )

    with app.app_context():
        print()
        print("===== DATABASE =====")

        inspector = inspect(db.engine)

        expected_tables = {
            "grade",
            "topic",
            "source_year",
            "question",
            "answer_option",
            "test_template",
            "competitor",
            "generated_test",
            "generated_test_question",
            "generated_test_answer",
            "competitor_attempt",
            "competitor_answer",
        }

        existing_tables = set(
            inspector.get_table_names()
        )

        check(
            "Required database tables exist",
            expected_tables.issubset(
                existing_tables
            ),
            str(
                sorted(
                    expected_tables
                    - existing_tables
                )
            ),
        )

        constraints = inspector.get_unique_constraints(
            "competitor_answer"
        )

        constraint = next(
            (
                item
                for item in constraints
                if item.get("name")
                == "uq_competitor_answer_selection"
            ),
            None,
        )

        check(
            "Multi-answer unique constraint exists",
            constraint is not None,
        )

        if constraint:
            check(
                "Multi-answer constraint has 3 columns",
                set(
                    constraint.get(
                        "column_names",
                        []
                    )
                )
                == {
                    "attempt_id",
                    "generated_test_question_id",
                    "generated_test_answer_id",
                },
                repr(
                    constraint.get(
                        "column_names"
                    )
                ),
            )

        check(
            "At least one grade exists",
            Grade.query.count() > 0,
        )

        check(
            "At least one source year exists",
            SourceYear.query.count() > 0,
        )

        check(
            "Topics table readable",
            Topic.query.count() >= 0,
        )

        check(
            "Questions table readable",
            Question.query.count() >= 0,
        )

        print()
        print("===== JINJA =====")

        try:
            template_names = (
                app.jinja_env.list_templates()
            )

            for template_name in template_names:
                app.jinja_env.get_template(
                    template_name
                )

            ok(
                f"All Jinja templates compile "
                f"({len(template_names)})"
            )

        except Exception as exc:
            fail(
                "Jinja template compilation",
                repr(exc),
            )

        print()
        print("===== ROUTES =====")

        rules = [
            rule
            for rule in app.url_map.iter_rules()
            if rule.endpoint != "static"
        ]

        endpoints = {
            rule.endpoint
            for rule in rules
        }

        expected_endpoints = {
            "index",
            "health",
            "admin.index",
            "admin.questions",
            "admin.question_new",
            "admin.question_detail",
            "admin.question_edit",
            "admin.question_import",
            "admin.results",
            "admin.result_detail",
            "admin.attempt_result_detail",
            "admin.competitors",
            "admin.competitor_create",
            "admin.competitor_edit",
            "admin_reference.grades",
            "admin_reference.topics",
            "admin_reference.source_years",
            "admin_templates.template_list",
            "admin_templates.template_new",
            "admin_templates.template_detail",
            "admin_templates.template_edit",
            "admin_templates.template_toggle_active",
            "admin_generated_tests.generated_test_list",
            "admin_generated_tests.generate_test",
            "admin_generated_tests.generated_test_detail",
            "admin_generated_tests.generated_test_activate",
            "admin_generated_tests.generated_test_close",
            "admin_generated_tests.generated_test_return_to_draft",
            "admin_media.question_image",
            "admin_media.question_image_upload",
            "admin_media.question_image_delete",
            "competitor.login",
            "competitor.logout",
            "competitor.dashboard",
            "competitor.set_language",
            "competitor.test_view",
        }

        missing_endpoints = (
            expected_endpoints - endpoints
        )

        check(
            "All expected endpoints registered",
            not missing_endpoints,
            repr(sorted(missing_endpoints)),
        )

        print(
            f"       Registered application routes: "
            f"{len(rules)}"
        )

        print()
        print("===== PUBLIC HTTP SMOKE =====")

        client = app.test_client()

        response = client.get("/health")

        check(
            "GET /health",
            response.status_code == 200,
            f"HTTP {response.status_code}",
        )

        if response.status_code == 200:
            payload = response.get_json()

            check(
                "Health application status",
                payload.get("status") == "ok",
                repr(payload),
            )

            check(
                "Health database status",
                payload.get(
                    "database",
                    {},
                ).get("status")
                == "ok",
                repr(payload),
            )

        response = client.get("/")

        check(
            "GET / redirects safely",
            response.status_code in {
                301,
                302,
                303,
                307,
                308,
            },
            f"HTTP {response.status_code}",
        )

        response = client.get(
            "/versenyzo/belepes"
        )

        check(
            "Competitor login page renders",
            response.status_code == 200,
            f"HTTP {response.status_code}",
        )

        print()
        print("===== ADMIN ROUTE SMOKE =====")

        admin = (
            Competitor.query
            .filter_by(
                is_admin=True,
                is_active=True,
            )
            .order_by(
                Competitor.id
            )
            .first()
        )

        check(
            "Active admin account exists",
            admin is not None,
        )

        if admin is not None:
            with client.session_transaction() as session:
                session["competitor_id"] = admin.id
                session["competitor_name"] = (
                    admin.full_name
                )
                session["is_admin"] = True
                session["language"] = "hu"

            safe_admin_urls = [
                "/admin/",
                "/admin/questions",
                "/admin/questions/new",
                "/admin/questions/import",
                "/admin/competitors",
                "/admin/competitors/new",
                "/admin/grades",
                "/admin/topics",
                "/admin/source-years",
                "/admin/test-templates/",
                "/admin/test-templates/new",
                "/admin/generated-tests/",
                "/admin/results",
            ]

            for url in safe_admin_urls:
                try:
                    response = client.get(url)

                    check(
                        f"GET {url}",
                        response.status_code == 200,
                        (
                            f"HTTP "
                            f"{response.status_code}"
                        ),
                    )

                except Exception as exc:
                    fail(
                        f"GET {url}",
                        repr(exc),
                    )

            question = (
                Question.query
                .order_by(Question.id)
                .first()
            )

            if question is not None:
                for url in [
                    (
                        f"/admin/questions/"
                        f"{question.id}"
                    ),
                    (
                        f"/admin/questions/"
                        f"{question.id}/edit"
                    ),
                ]:
                    try:
                        response = client.get(url)

                        check(
                            f"GET {url}",
                            response.status_code
                            == 200,
                            (
                                f"HTTP "
                                f"{response.status_code}"
                            ),
                        )

                    except Exception as exc:
                        fail(
                            f"GET {url}",
                            repr(exc),
                        )

            template = (
                TestTemplate.query
                .order_by(TestTemplate.id)
                .first()
            )

            if template is not None:
                for url in [
                    (
                        f"/admin/test-templates/"
                        f"{template.id}"
                    ),
                    (
                        f"/admin/test-templates/"
                        f"{template.id}/edit"
                    ),
                ]:
                    try:
                        response = client.get(url)

                        check(
                            f"GET {url}",
                            response.status_code
                            == 200,
                            (
                                f"HTTP "
                                f"{response.status_code}"
                            ),
                        )

                    except Exception as exc:
                        fail(
                            f"GET {url}",
                            repr(exc),
                        )

            generated_test = (
                GeneratedTest.query
                .order_by(GeneratedTest.id)
                .first()
            )

            if generated_test is not None:
                url = (
                    "/admin/generated-tests/"
                    f"{generated_test.id}"
                )

                try:
                    response = client.get(url)

                    check(
                        f"GET {url}",
                        response.status_code == 200,
                        (
                            f"HTTP "
                            f"{response.status_code}"
                        ),
                    )

                except Exception as exc:
                    fail(
                        f"GET {url}",
                        repr(exc),
                    )

        print()
        print("===== MULTI-CORRECT MODEL =====")

        multi_question = (
            Question.query
            .join(Question.answer_options)
            .group_by(Question.id)
            .having(
                db.func.sum(
                    db.case(
                        (
                            AnswerOption.is_correct
                            .is_(True),
                            1,
                        ),
                        else_=0,
                    )
                )
                >= 2
            )
            .order_by(Question.id.desc())
            .first()
        )

        if multi_question is None:
            print(
                "[SKIP] No existing multi-correct "
                "question yet"
            )
        else:
            correct_positions = {
                answer.original_position
                for answer
                in multi_question.answer_options
                if answer.is_correct
            }

            check(
                "Existing multi-correct question "
                "has >=2 correct answers",
                len(correct_positions) >= 2,
                repr(correct_positions),
            )

        print()
        print("===== GENERATED ANSWER SCORING =====")

        generated_question = None

        for candidate in (
            GeneratedTestQuestion.query
            .order_by(
                GeneratedTestQuestion.id.desc()
            )
            .all()
        ):
            correct_answers = [
                answer
                for answer
                in candidate.generated_answers
                if answer.answer_option.is_correct
            ]

            if len(correct_answers) >= 2:
                generated_question = candidate
                break

        if generated_question is None:
            print(
                "[SKIP] No generated multi-correct "
                "question exists yet"
            )
        else:
            correct_ids = {
                answer.id
                for answer
                in generated_question.generated_answers
                if answer.answer_option.is_correct
            }

            wrong_ids = {
                answer.id
                for answer
                in generated_question.generated_answers
                if not answer.answer_option.is_correct
            }

            check(
                "Exact correct set scores",
                score_question(
                    generated_question,
                    correct_ids,
                ),
            )

            one_missing = set(correct_ids)

            if one_missing:
                one_missing.pop()

            check(
                "Missing correct answer fails",
                not score_question(
                    generated_question,
                    one_missing,
                ),
            )

            if wrong_ids:
                one_extra = (
                    set(correct_ids)
                    | {next(iter(wrong_ids))}
                )

                check(
                    "Extra wrong answer fails",
                    not score_question(
                        generated_question,
                        one_extra,
                    ),
                )

            all_ids = {
                answer.id
                for answer
                in generated_question.generated_answers
            }

            if all_ids != correct_ids:
                check(
                    "Selecting all answers fails "
                    "when not all are correct",
                    not score_question(
                        generated_question,
                        all_ids,
                    ),
                )

        print()
        print("===== TEMPLATE CONTENT =====")

        test_template_source = (
            ROOT
            / "app/templates/competitor/"
            "test_view.html"
        ).read_text(
            encoding="utf-8"
        )

        check(
            "Competitor answers use checkboxes",
            'type="checkbox"'
            in test_template_source,
        )

        check(
            "Competitor test contains no radio input",
            'type="radio"'
            not in test_template_source,
        )

        check(
            "Question answer fields are per question",
            (
                'name="question_'
                '{{ generated_question.id }}"'
            )
            in test_template_source,
        )

        question_form_source = (
            ROOT
            / "app/templates/admin/"
            "question_form.html"
        ).read_text(
            encoding="utf-8"
        )

        check(
            "Question form is multipart",
            (
                'enctype="multipart/form-data"'
                in question_form_source
            ),
        )

        check(
            "Question form uses multi-correct field",
            (
                'name="correct_answers"'
                in question_form_source
            ),
        )

        check(
            "Question form correct answers "
            "are checkboxes",
            (
                'type="checkbox"'
                in question_form_source
            ),
        )

        print()
        print("===== CSV MULTI-CORRECT SOURCE =====")

        admin_source = (
            ROOT
            / "app/routes/admin.py"
        ).read_text(
            encoding="utf-8"
        )

        check(
            "CSV parser accepts pipe separator",
            (
                '["helyes"].split("|")'
                in admin_source
            ),
        )

        check(
            "CSV parser stores correct_answers set",
            (
                '"correct_answers"'
                in admin_source
            ),
        )

        print()
        print("===== TRANSLATIONS =====")

        try:
            from babel.messages.pofile import read_po

            po_path = (
                ROOT
                / "translations/en/LC_MESSAGES/"
                "messages.po"
            )

            with po_path.open(
                "r",
                encoding="utf-8",
            ) as file_handle:
                catalog = read_po(file_handle)

            empty = []
            fuzzy = []

            for message in catalog:
                if not message.id:
                    continue

                if not message.string:
                    empty.append(message.id)

                if "fuzzy" in message.flags:
                    fuzzy.append(message.id)

            check(
                "English translations have no "
                "empty entries",
                not empty,
                repr(empty[:10]),
            )

            check(
                "English translations have no "
                "fuzzy entries",
                not fuzzy,
                repr(fuzzy[:10]),
            )

        except Exception as exc:
            fail(
                "Translation catalog audit",
                repr(exc),
            )

        db.session.rollback()

    print()
    print("=" * 72)
    print(
        f"RESULT: {passed} PASS, "
        f"{failed} FAIL"
    )
    print("=" * 72)

    if failed:
        print("FULL TEST FAILED")
        return 1

    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
