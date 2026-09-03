#!/usr/bin/env python3

from pathlib import Path


ROOT = Path("/opt/feladatverseny")

ROUTE = ROOT / "app/routes/competitor.py"
DASHBOARD = (
    ROOT
    / "app/templates/competitor/dashboard.html"
)
TEST_VIEW = (
    ROOT
    / "app/templates/competitor/test_view.html"
)


def replace_once(
    text: str,
    old: str,
    new: str,
    label: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly 1 match, "
            f"found {count}"
        )

    return text.replace(
        old,
        new,
        1,
    )


text = ROUTE.read_text(
    encoding="utf-8"
)

replacements = [
    (
        '''        flash(
            "Az oldal megtekintéséhez jelentkezz be.",
            "error",
        )''',
        '''        flash(
            _(
                "Az oldal megtekintéséhez "
                "jelentkezz be."
            ),
            "error",
        )''',
        "dashboard login required",
    ),
    (
        '''        flash(
            "A felhasználói fiók nem érhető el.",
            "error",
        )''',
        '''        flash(
            _(
                "A felhasználói fiók "
                "nem érhető el."
            ),
            "error",
        )''',
        "unavailable account",
        2,
    ),
    (
        '''        flash(
            "A feladatsor megtekintéséhez jelentkezz be.",
            "error",
        )''',
        '''        flash(
            _(
                "A feladatsor megtekintéséhez "
                "jelentkezz be."
            ),
            "error",
        )''',
        "test login required",
    ),
    (
        '''        flash(
            "Ez a feladatsor számodra nem érhető el.",
            "error",
        )''',
        '''        flash(
            _(
                "Ez a feladatsor számodra "
                "nem érhető el."
            ),
            "error",
        )''',
        "test unavailable",
    ),
    (
        '''            flash(
                "A forduló lezárult, ezért a válaszok "
                "már nem módosíthatók.",
                "error",
            )''',
        '''            flash(
                _(
                    "A forduló lezárult, ezért "
                    "a válaszok már nem "
                    "módosíthatók."
                ),
                "error",
            )''',
        "closed test modification",
    ),
    (
        '''            flash(
                "A feladatsor már le van zárva, ezért nem módosítható.",
                "error",
            )''',
        '''            flash(
                _(
                    "A feladatsor már le van zárva, "
                    "ezért nem módosítható."
                ),
                "error",
            )''',
        "submitted test modification",
    ),
    (
        '''            flash(
                "A feladatsor végleges beküldése sikerült.",
                "success",
            )''',
        '''            flash(
                _(
                    "A feladatsor végleges "
                    "beküldése sikerült."
                ),
                "success",
            )''',
        "submit success",
    ),
    (
        '''            flash(
                "A válaszok mentése sikerült.",
                "success",
            )''',
        '''            flash(
                _("A válaszok mentése sikerült."),
                "success",
            )''',
        "save success",
    ),
]

for replacement in replacements:
    if len(replacement) == 3:
        old, new, label = replacement
        expected_count = 1
    else:
        old, new, label, expected_count = replacement

    count = text.count(old)

    if count != expected_count:
        raise RuntimeError(
            f"{label}: expected exactly "
            f"{expected_count} match(es), "
            f"found {count}"
        )

    text = text.replace(
        old,
        new,
        expected_count,
    )

ROUTE.write_text(
    text,
    encoding="utf-8",
)


DASHBOARD.write_text(
    r'''{% extends "base.html" %}

{% block title %}
    {{ _("Versenyzői kezdőlap") }}
{% endblock %}

{% block content %}
<div class="page-header">
    <div>
        <h1>
            {{
                _(
                    "Üdvözlünk, %(name)s!",
                    name=competitor.full_name
                )
            }}
        </h1>

        <p>
            {{
                _(
                    "%(grade)s. évfolyam",
                    grade=competitor.grade.grade_number
                )
            }}
        </p>
    </div>

    <div>
        <a
            class="button button-secondary"
            href="{{ url_for('competitor.logout') }}"
        >
            {{ _("Kijelentkezés") }}
        </a>
    </div>
</div>

<section class="card">
    <h2>
        {{ _("Elérhető feladatsorok") }}
    </h2>

    {% if active_tests %}
        <div class="test-card-list">
            {% for generated_test in active_tests %}
                <article class="test-card">
                    <div class="test-card-content">
                        <h3>
                            {{ generated_test.name }}
                        </h3>

                        <p>
                            {{ _("Feladatok száma:") }}
                            <strong>
                                {{
                                    generated_test
                                    .generated_questions
                                    | length
                                }}
                            </strong>
                        </p>

                        <p>
                            {{ _("Létrehozva:") }}
                            {{
                                generated_test
                                .created_at
                                .strftime(
                                    "%Y-%m-%d %H:%M"
                                )
                            }}
                        </p>
                    </div>

                    <div class="test-card-actions">
                        <a
                            class="button"
                            href="{{ url_for(
                                'competitor.test_view',
                                test_id=generated_test.id
                            ) }}"
                        >
                            {{
                                _(
                                    "Feladatsor "
                                    "megnyitása"
                                )
                            }}
                        </a>
                    </div>
                </article>
            {% endfor %}
        </div>
    {% else %}
        <p>
            {{
                _(
                    "Jelenleg nincs az évfolyamodhoz "
                    "elérhető aktív feladatsor."
                )
            }}
        </p>
    {% endif %}
</section>

<section class="card">
    <h2>
        {{ _("Korábbi eredményeim") }}
    </h2>

    {% if result_rows %}
        <div class="table-wrapper">
            <table class="data-table results-table">
                <thead>
                    <tr>
                        <th>
                            {{ _("Forduló") }}
                        </th>

                        <th class="table-number">
                            {{ _("Helyezés") }}
                        </th>

                        <th class="table-number">
                            {{ _("Feladatok") }}
                        </th>

                        <th class="table-number">
                            {{ _("Pontszám") }}
                        </th>

                        <th class="table-number">
                            {{ _("Eredmény") }}
                        </th>

                        <th>
                            {{ _("Beadás") }}
                        </th>

                        <th class="table-actions">
                            {{ _("Művelet") }}
                        </th>
                    </tr>
                </thead>

                <tbody>
                    {% for row in result_rows %}
                        <tr>
                            <td class="result-test-name">
                                {{
                                    row.attempt
                                    .generated_test
                                    .name
                                }}
                            </td>

                            <td class="table-number result-rank">
                                {% if row.rank is not none %}
                                    {{ row.rank }}.
                                {% else %}
                                    –
                                {% endif %}
                            </td>

                            <td class="table-number">
                                {{ row.question_count }}
                            </td>

                            <td class="table-number">
                                <strong>
                                    {{ row.score }}
                                    /
                                    {{ row.question_count }}
                                </strong>
                            </td>

                            <td class="table-number">
                                {{
                                    "%.1f"
                                    | format(
                                        row.percentage
                                    )
                                }}
                                %
                            </td>

                            <td>
                                {% if row.attempt.submitted_at %}
                                    {{
                                        row.attempt
                                        .submitted_at
                                        .strftime(
                                            "%Y.%m.%d. %H:%M"
                                        )
                                    }}
                                {% else %}
                                    <span
                                        class="
                                            status-badge
                                            status-inactive
                                        "
                                    >
                                        {{
                                            _(
                                                "Nem adta be"
                                            )
                                        }}
                                    </span>
                                {% endif %}
                            </td>

                            <td class="table-actions">
                                <a
                                    class="
                                        button
                                        button-secondary
                                    "
                                    href="{{ url_for(
                                        'competitor.test_view',
                                        test_id=(
                                            row.attempt
                                            .generated_test
                                            .id
                                        )
                                    ) }}"
                                >
                                    {{
                                        _(
                                            "Feladatlap "
                                            "megtekintése"
                                        )
                                    }}
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <p>
            {{
                _(
                    "Még nincs lezárt forduló, "
                    "amelyben részt vettél."
                )
            }}
        </p>
    {% endif %}
</section>
{% endblock %}
''',
    encoding="utf-8",
)


TEST_VIEW.write_text(
    r'''{% extends "base.html" %}

{% block title %}
    {{ generated_test.name }}
{% endblock %}

{% block content %}

<div class="page-header">
    <div>
        <h1>
            {{ generated_test.name }}
        </h1>

        <p>
            {{ _("Versenyző:") }}
            <strong>
                {{ competitor.full_name }}
            </strong>
        </p>

        <p>
            {{ _("Feladatok száma:") }}
            <strong>
                {{ test_questions | length }}
            </strong>
        </p>

        {% if attempt.started_at %}
            <p>
                {{ _("Megkezdve:") }}
                <strong>
                    {{
                        attempt.started_at.strftime(
                            "%Y.%m.%d. %H:%M:%S"
                        )
                    }}
                </strong>
            </p>
        {% endif %}

        {% if attempt.status == "submitted" %}
            {% if attempt.submitted_at %}
                <p>
                    {{ _("Befejezve:") }}
                    <strong>
                        {{
                            attempt.submitted_at.strftime(
                                "%Y.%m.%d. %H:%M:%S"
                            )
                        }}
                    </strong>
                </p>
            {% endif %}

            {% if completion_time %}
                <p>
                    {{ _("Kitöltési idő:") }}
                    <strong>
                        {{ completion_time }}
                    </strong>
                </p>
            {% endif %}
        {% endif %}

        {% if results_visible %}
            <p>
                <strong>
                    {{
                        _(
                            "A forduló lezárult. "
                            "A válaszok már nem "
                            "módosíthatók."
                        )
                    }}
                </strong>
            </p>

            <p>
                {{ _("Eredmény:") }}
                <strong>
                    {{ correct_answer_count }}
                    /
                    {{ total_question_count }}
                    {{ _("pont") }}
                </strong>
            </p>
        {% endif %}
    </div>

    <div>
        <a
            class="button button-secondary"
            href="{{ url_for(
                'competitor.dashboard'
            ) }}"
        >
            {{ _("Vissza") }}
        </a>
    </div>
</div>

<form
    class="competitor-test-form"
    method="post"
>
    {% for generated_question in test_questions %}

        <section class="card question-card">

            <div class="question-number">
                {{
                    _(
                        "%(position)s. feladat",
                        position=(
                            generated_question
                            .display_position
                        )
                    )
                }}
            </div>

            <div class="question-text">
                {{
                    generated_question
                    .question
                    .question_text
                }}
            </div>

            <div class="answer-options">

                {% for generated_answer
                    in generated_question.generated_answers %}

                    <label class="answer-option">

                        <input
                            class="answer-radio"
                            type="radio"
                            name="question_{{ generated_question.id }}"
                            value="{{ generated_answer.id }}"
                            {% if saved_answers.get(
                                generated_question.id
                            ) == generated_answer.id %}
                                checked
                            {% endif %}
                            {% if (
                                attempt.status == "submitted"
                                or results_visible
                            ) %}
                                disabled
                            {% endif %}
                        >

                        <span class="answer-marker">
                            {% if generated_answer.display_position == 1 %}
                                A
                            {% elif generated_answer.display_position == 2 %}
                                B
                            {% elif generated_answer.display_position == 3 %}
                                C
                            {% elif generated_answer.display_position == 4 %}
                                D
                            {% elif generated_answer.display_position == 5 %}
                                E
                            {% endif %}
                        </span>

                        <span class="answer-content">
                            {{
                                generated_answer
                                .answer_option
                                .answer_text
                                or ""
                            }}

                            {% if results_visible %}

                                {% set is_selected =
                                    saved_answers.get(
                                        generated_question.id
                                    )
                                    == generated_answer.id
                                %}

                                {% if (
                                    is_selected
                                    and generated_answer
                                        .answer_option
                                        .is_correct
                                ) %}
                                    <strong>
                                        {{ _("✓ Jó válasz") }}
                                    </strong>

                                {% elif is_selected %}
                                    <strong>
                                        {{ _("✗ Ezt jelölted") }}
                                    </strong>

                                {% elif (
                                    generated_answer
                                    .answer_option
                                    .is_correct
                                ) %}
                                    <strong>
                                        {{
                                            _(
                                                "✓ Helyes válasz"
                                            )
                                        }}
                                    </strong>
                                {% endif %}

                            {% endif %}
                        </span>

                    </label>

                {% endfor %}

            </div>

        </section>

    {% else %}

        <section class="card">
            <p>
                {{
                    _(
                        "Ebben a feladatsorban "
                        "nincs kérdés."
                    )
                }}
            </p>
        </section>

    {% endfor %}

    {% if (
        attempt.status == "in_progress"
        and not results_visible
    ) %}
        <div class="test-actions">

            <button
                class="button button-secondary"
                type="submit"
                name="action"
                value="save"
            >
                {{ _("Válaszok mentése") }}
            </button>

            <button
                class="button"
                type="submit"
                name="action"
                value="submit"
                onclick='return confirm({{
                    _(
                        "Biztosan véglegesen "
                        "beküldöd a feladatsort? "
                        "A beküldés után a válaszok "
                        "már nem módosíthatók."
                    ) | tojson
                }});'
            >
                {{
                    _(
                        "Feladatsor végleges "
                        "beküldése"
                    )
                }}
            </button>

        </div>
    {% else %}
        <section class="card">
            <p>
                {{
                    _(
                        "Ez a feladatsor már le van "
                        "zárva, ezért a válaszok "
                        "nem módosíthatók."
                    )
                }}
            </p>
        </section>
    {% endif %}

</form>

{% endblock %}
''',
    encoding="utf-8",
)

print("Competitor i18n migration completed.")
