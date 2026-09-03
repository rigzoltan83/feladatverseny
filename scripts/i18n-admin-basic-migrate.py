#!/usr/bin/env python3

from pathlib import Path


ROOT = Path("/opt/feladatverseny/app/templates/admin")


files = {
    "grades.html": r'''{% extends "base.html" %}

{% block title %}
    {{ _("Évfolyamok – Feladatverseny") }}
{% endblock %}

{% block content %}
    <section class="page-header">
        <h1>{{ _("Évfolyamok") }}</h1>

        <p>
            {{
                _(
                    "Az adatbázisban jelenleg "
                    "elérhető évfolyamok."
                )
            }}
        </p>
    </section>

    <section class="card">
        <table class="data-table">
            <thead>
                <tr>
                    <th>{{ _("Azonosító") }}</th>
                    <th>{{ _("Évfolyam") }}</th>
                    <th>{{ _("Megnevezés") }}</th>
                </tr>
            </thead>

            <tbody>
                {% for grade in grades %}
                    <tr>
                        <td>{{ grade.id }}</td>
                        <td>{{ grade.grade_number }}</td>
                        <td>{{ grade.name }}</td>
                    </tr>
                {% else %}
                    <tr>
                        <td colspan="3">
                            {{
                                _(
                                    "Nincs még rögzített "
                                    "évfolyam."
                                )
                            }}
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
{% endblock %}
''',

    "topics.html": r'''{% extends "base.html" %}

{% block title %}
    {{ _("Témakörök – Feladatverseny") }}
{% endblock %}

{% block content %}
    <section class="page-header">
        <h1>{{ _("Témakörök") }}</h1>

        <p>
            {{
                _(
                    "A feladatokhoz rendelhető "
                    "témakörök."
                )
            }}
        </p>
    </section>

    <section class="card">
        <table class="data-table">
            <thead>
                <tr>
                    <th>{{ _("Azonosító") }}</th>
                    <th>{{ _("Megnevezés") }}</th>
                    <th>{{ _("Állapot") }}</th>
                </tr>
            </thead>

            <tbody>
                {% for topic in topics %}
                    <tr>
                        <td>{{ topic.id }}</td>
                        <td>{{ topic.name }}</td>

                        <td>
                            {% if topic.is_active %}
                                {{ _("Aktív") }}
                            {% else %}
                                {{ _("Inaktív") }}
                            {% endif %}
                        </td>
                    </tr>
                {% else %}
                    <tr>
                        <td colspan="3">
                            {{
                                _(
                                    "Nincs még rögzített "
                                    "témakör."
                                )
                            }}
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
{% endblock %}
''',

    "source_years.html": r'''{% extends "base.html" %}

{% block title %}
    {{ _("Forrásévek – Feladatverseny") }}
{% endblock %}

{% block content %}
    <section class="page-header">
        <h1>{{ _("Forrásévek") }}</h1>

        <p>
            {{
                _(
                    "A korábbi feladatsorokhoz "
                    "tartozó versenyévek."
                )
            }}
        </p>
    </section>

    <section class="card">
        <table class="data-table">
            <thead>
                <tr>
                    <th>{{ _("Azonosító") }}</th>
                    <th>{{ _("Év") }}</th>
                    <th>{{ _("Állapot") }}</th>
                </tr>
            </thead>

            <tbody>
                {% for source_year in source_years %}
                    <tr>
                        <td>{{ source_year.id }}</td>
                        <td>{{ source_year.year_number }}</td>

                        <td>
                            {% if source_year.is_active %}
                                {{ _("Aktív") }}
                            {% else %}
                                {{ _("Inaktív") }}
                            {% endif %}
                        </td>
                    </tr>
                {% else %}
                    <tr>
                        <td colspan="3">
                            {{
                                _(
                                    "Nincs még rögzített "
                                    "forrásév."
                                )
                            }}
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
{% endblock %}
''',

    "index.html": r'''{% extends "base.html" %}

{% block title %}
    {{ _("Adminisztráció – Feladatverseny") }}
{% endblock %}

{% block content %}
<section class="page-header">
    <div class="page-header-row">
        <div>
            <h1>{{ _("Adminisztráció") }}</h1>

            <p>
                {{
                    _(
                        "A Feladatverseny adatainak "
                        "és működésének kezelése."
                    )
                }}
            </p>
        </div>

        <a
            href="{{ url_for('competitor.dashboard') }}"
            class="button"
        >
            {{ _("← Versenyzői oldal") }}
        </a>
    </div>
</section>

<div class="admin-grid">
    <a
        class="admin-card"
        href="{{ url_for('admin_reference.grades') }}"
    >
        <h2>{{ _("Évfolyamok") }}</h2>
        <p>{{ _("Évfolyamok kezelése.") }}</p>
    </a>

    <a
        class="admin-card"
        href="{{ url_for('admin_reference.topics') }}"
    >
        <h2>{{ _("Témakörök") }}</h2>
        <p>
            {{
                _(
                    "A feladatok témaköreinek "
                    "kezelése."
                )
            }}
        </p>
    </a>

    <a
        class="admin-card"
        href="{{ url_for('admin_reference.source_years') }}"
    >
        <h2>{{ _("Forrásévek") }}</h2>
        <p>
            {{ _("A korábbi versenyévek kezelése.") }}
        </p>
    </a>

    <a
        class="admin-card"
        href="{{ url_for('admin.questions') }}"
    >
        <h2>{{ _("Feladatok") }}</h2>
        <p>
            {{
                _(
                    "Feladatok és válaszlehetőségek "
                    "kezelése."
                )
            }}
        </p>
    </a>

    <a
        class="admin-card"
        href="{{ url_for('admin.competitors') }}"
    >
        <h2>{{ _("Versenyzők") }}</h2>
        <p>
            {{
                _(
                    "Versenyzők és felhasználók "
                    "kezelése."
                )
            }}
        </p>
    </a>

    <a
        class="admin-card"
        href="{{
            url_for(
                'admin_templates.template_list'
            )
        }}"
    >
        <h2>{{ _("Feladatsorok") }}</h2>
        <p>
            {{
                _(
                    "Tesztsablonok és generálási "
                    "szabályok."
                )
            }}
        </p>
    </a>

    <a
        class="admin-card"
        href="{{
            url_for(
                'admin_generated_tests.generated_test_list'
            )
        }}"
    >
        <h2>{{ _("Generált feladatsorok") }}</h2>

        <p>
            {{
                _(
                    "Létrehozott tesztek, "
                    "aktiválás és lezárás."
                )
            }}
        </p>
    </a>

    <a
        class="admin-card"
        href="{{ url_for('admin.results') }}"
    >
        <h2>{{ _("Eredmények") }}</h2>

        <p>
            {{
                _(
                    "Lezárt fordulók, kitöltések "
                    "és pontszámok."
                )
            }}
        </p>
    </a>
</div>
{% endblock %}
''',

    "competitors.html": r'''{% extends "base.html" %}

{% block title %}
    {{ _("Versenyzők") }}
{% endblock %}

{% block content %}
<div class="page-header">
    <div>
        <h1>{{ _("Versenyzők") }}</h1>

        <p>
            {{ _("Regisztrált versenyzők kezelése.") }}
        </p>
    </div>

    <div>
        <a
            class="button"
            href="{{ url_for('admin.competitor_create') }}"
        >
            {{ _("Új versenyző") }}
        </a>
    </div>
</div>

<section class="card question-filter-card">
    <form
        method="get"
        action="{{ url_for('admin.competitors') }}"
        class="question-search-form"
    >
        <div class="form-group question-search-field">
            <label for="q">
                {{ _("Keresés") }}
            </label>

            <input
                id="q"
                name="q"
                type="search"
                value="{{ search_text }}"
                placeholder="{{
                    _('Név vagy felhasználónév...')
                }}"
            >
        </div>

        <div class="question-search-actions">
            <button
                class="button"
                type="submit"
            >
                {{ _("Keresés") }}
            </button>

            {% if search_text %}
                <a
                    class="button button-secondary"
                    href="{{ url_for('admin.competitors') }}"
                >
                    {{ _("Keresés törlése") }}
                </a>
            {% endif %}
        </div>
    </form>
</section>

<p class="list-summary">
    <strong>{{ pagination.total }}</strong>
    {{ _("versenyző található.") }}

    {% if pagination.total %}
        {{ _("Megjelenítve:") }}
        {{ pagination.first }}–{{ pagination.last }}.
    {% endif %}
</p>

<div class="table-wrapper">
    <table class="data-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>{{ _("Teljes név") }}</th>
                <th>{{ _("Felhasználónév") }}</th>
                <th>{{ _("Évfolyam") }}</th>
                <th>{{ _("Állapot") }}</th>
                <th>{{ _("Létrehozva") }}</th>
                <th>{{ _("Műveletek") }}</th>
            </tr>
        </thead>

        <tbody>
            {% for competitor in competitors %}
                <tr>
                    <td>
                        {{ competitor.id }}
                    </td>

                    <td>
                        {{ competitor.full_name }}
                    </td>

                    <td>
                        {{ competitor.username }}
                    </td>

                    <td>
                        {{
                            _(
                                "%(grade)s. évfolyam",
                                grade=(
                                    competitor.grade
                                    .grade_number
                                )
                            )
                        }}
                    </td>

                    <td>
                        {% if competitor.is_active %}
                            <span
                                class="
                                    status-badge
                                    status-active
                                "
                            >
                                {{ _("Aktív") }}
                            </span>
                        {% else %}
                            <span
                                class="
                                    status-badge
                                    status-inactive
                                "
                            >
                                {{ _("Inaktív") }}
                            </span>
                        {% endif %}
                    </td>

                    <td>
                        {{
                            competitor.created_at.strftime(
                                "%Y-%m-%d %H:%M"
                            )
                        }}
                    </td>

                    <td>
                        <a
                            class="button button-secondary"
                            href="{{ url_for(
                                'admin.competitor_edit',
                                competitor_id=competitor.id
                            ) }}"
                        >
                            {{ _("Szerkesztés") }}
                        </a>
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td
                        colspan="7"
                        class="empty-table-cell"
                    >
                        {{
                            _(
                                "Nincs megjeleníthető "
                                "versenyző."
                            )
                        }}
                    </td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

{% if pagination.pages > 1 %}
    <nav class="pagination">
        {% if pagination.has_prev %}
            <a
                class="button button-secondary"
                href="{{ url_for(
                    'admin.competitors',
                    page=pagination.prev_num,
                    q=search_text
                ) }}"
            >
                {{ _("Előző") }}
            </a>
        {% endif %}

        <span class="pagination-info">
            {{
                _(
                    "%(page)s / %(pages)s. oldal",
                    page=pagination.page,
                    pages=pagination.pages
                )
            }}
        </span>

        {% if pagination.has_next %}
            <a
                class="button button-secondary"
                href="{{ url_for(
                    'admin.competitors',
                    page=pagination.next_num,
                    q=search_text
                ) }}"
            >
                {{ _("Következő") }}
            </a>
        {% endif %}
    </nav>
{% endif %}
{% endblock %}
''',
}


for name, content in files.items():
    path = ROOT / name

    if not path.is_file():
        raise SystemExit(
            f"ERROR: missing template: {path}"
        )

    path.write_text(
        content,
        encoding="utf-8",
    )

    print(
        f"UPDATED: {path}"
    )

print(
    f"OK: {len(files)} admin templates migrated"
)
