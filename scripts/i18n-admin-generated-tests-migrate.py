#!/usr/bin/env python3

from pathlib import Path
import re


ROOT = Path("/opt/feladatverseny")

ROUTE = ROOT / "app/routes/admin_generated_tests.py"
LIST = ROOT / "app/templates/admin/generated_tests.html"
DETAIL = ROOT / "app/templates/admin/generated_test_detail.html"


def replace_exact(text, old, new, expected=1, label=""):
    count = text.count(old)

    if count != expected:
        raise RuntimeError(
            f"{label}: expected {expected}, "
            f"found {count}: {old!r}"
        )

    return text.replace(old, new)


def replace_line(text, old, new, expected=1, label=""):
    pattern = re.compile(
        rf"^([ \t]*){re.escape(old)}[ \t]*$",
        re.MULTILINE,
    )

    matches = pattern.findall(text)

    if len(matches) != expected:
        raise RuntimeError(
            f"{label}: expected {expected}, "
            f"found {len(matches)} line(s): "
            f"{old!r}"
        )

    return pattern.sub(
        lambda m: m.group(1) + new,
        text,
    )


# ============================================================
# ROUTE
# ============================================================

route = ROUTE.read_text(encoding="utf-8")

route = replace_exact(
    route,
    """from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
""",
    """from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from flask_babel import gettext as _
""",
    label="route import",
)

route_replacements = [
    (
        """(
                "Inaktív tesztsablonból "
                "nem generálható feladatsor."
            )""",
        """_(
                "Inaktív tesztsablonból "
                "nem generálható feladatsor."
            )""",
        1,
    ),
    (
        """(
                "A generálás megszakadt, mert "
                "ismétlődő feladat került a listába."
            )""",
        """_(
                "A generálás megszakadt, mert "
                "ismétlődő feladat került a listába."
            )""",
        1,
    ),
    (
        """(
                "Lezárt feladatsor nem "
                "aktiválható újra."
            )""",
        """_(
                "Lezárt feladatsor nem "
                "aktiválható újra."
            )""",
        1,
    ),
    (
        '"A feladatsor már aktív."',
        '_("A feladatsor már aktív.")',
        1,
    ),
    (
        '"A feladatsort aktiváltuk."',
        '_("A feladatsort aktiváltuk.")',
        1,
    ),
    (
        '"A feladatsor már le van zárva."',
        '_("A feladatsor már le van zárva.")',
        1,
    ),
    (
        '"A feladatsort lezártuk."',
        '_("A feladatsort lezártuk.")',
        1,
    ),
    (
        """(
                "Lezárt feladatsor nem "
                "állítható vissza piszkozatba."
            )""",
        """_(
                "Lezárt feladatsor nem "
                "állítható vissza piszkozatba."
            )""",
        1,
    ),
    (
        '"A feladatsor már piszkozat."',
        '_("A feladatsor már piszkozat.")',
        1,
    ),
    (
        """(
                "A feladatsort visszaállítottuk "
                "piszkozat állapotba."
            )""",
        """_(
                "A feladatsort visszaállítottuk "
                "piszkozat állapotba."
            )""",
        1,
    ),
]

for old, new, expected in route_replacements:
    route = replace_exact(
        route,
        old,
        new,
        expected,
        "route",
    )


# Dynamic insufficient-question flash
route = replace_exact(
    route,
    """(
                "Nincs elegendő megfelelő feladat. "
                f"Elérhető: {len(candidates)}, "
                f"szükséges: {template.question_count}."
            )""",
    """_(
                "Nincs elegendő megfelelő feladat. "
                "Elérhető: %(available)s, "
                "szükséges: %(required)s.",
                available=len(candidates),
                required=template.question_count,
            )""",
    label="route candidate count",
)


# Dynamic generation-success flash
route = replace_exact(
    route,
    """(
            f"A feladatsor elkészült "
            f"{template.question_count} feladattal."
        )""",
    """_(
            "A feladatsor elkészült "
            "%(count)s feladattal.",
            count=template.question_count,
        )""",
    label="route generation success",
)


# ============================================================
# LIST TEMPLATE
# ============================================================

list_text = LIST.read_text(encoding="utf-8")

list_lines = [
    (
        "Generált feladatsorok – Feladatverseny",
        '{{ _("Generált feladatsorok – Feladatverseny") }}',
        1,
    ),
    (
        "<h1>Generált feladatsorok</h1>",
        '<h1>{{ _("Generált feladatsorok") }}</h1>',
        1,
    ),
    (
        "<th>Név</th>",
        '<th>{{ _("Név") }}</th>',
        1,
    ),
    (
        "<th>Sablon</th>",
        '<th>{{ _("Sablon") }}</th>',
        1,
    ),
    (
        "<th>Feladatok</th>",
        '<th>{{ _("Feladatok") }}</th>',
        1,
    ),
    (
        "<th>Állapot</th>",
        '<th>{{ _("Állapot") }}</th>',
        1,
    ),
    (
        "<th>Létrehozva</th>",
        '<th>{{ _("Létrehozva") }}</th>',
        1,
    ),
    (
        "<th>Művelet</th>",
        '<th>{{ _("Művelet") }}</th>',
        1,
    ),
    (
        "Piszkozat",
        '{{ _("Piszkozat") }}',
        1,
    ),
    (
        "Aktív",
        '{{ _("Aktív") }}',
        1,
    ),
    (
        "Lezárt",
        '{{ _("Lezárt") }}',
        1,
    ),
    (
        "Megnyitás",
        '{{ _("Megnyitás") }}',
        1,
    ),
]

for old, new, expected in list_lines:
    list_text = replace_line(
        list_text,
        old,
        new,
        expected,
        "list",
    )

list_text = replace_exact(
    list_text,
    """A sablonok alapján létrehozott
            konkrét tesztek.""",
    """{{ _("A sablonok alapján létrehozott konkrét tesztek.") }}""",
    label="list description",
)

list_text = replace_exact(
    list_text,
    """Nincs még generált
                            feladatsor.""",
    """{{ _("Nincs még generált feladatsor.") }}""",
    label="list empty",
)


# ============================================================
# DETAIL TEMPLATE
# ============================================================

detail = DETAIL.read_text(encoding="utf-8")

detail_lines = [
    (
        "Generált feladatsor ellenőrzése.",
        '{{ _("Generált feladatsor ellenőrzése.") }}',
        1,
    ),
    (
        "Aktiválás",
        '{{ _("Aktiválás") }}',
        1,
    ),
    (
        "Lezárás",
        '{{ _("Lezárás") }}',
        2,
    ),
    (
        "Vissza piszkozatba",
        '{{ _("Vissza piszkozatba") }}',
        1,
    ),
    (
        "Vissza a sablonhoz",
        '{{ _("Vissza a sablonhoz") }}',
        1,
    ),
    (
        "Generált feladatsorok",
        '{{ _("Generált feladatsorok") }}',
        1,
    ),
    (
        "<h2>Alapadatok</h2>",
        '<h2>{{ _("Alapadatok") }}</h2>',
        1,
    ),
    (
        "<dt>Azonosító</dt>",
        '<dt>{{ _("Azonosító") }}</dt>',
        1,
    ),
    (
        "<dt>Sablon</dt>",
        '<dt>{{ _("Sablon") }}</dt>',
        1,
    ),
    (
        "<dt>Állapot</dt>",
        '<dt>{{ _("Állapot") }}</dt>',
        1,
    ),
    (
        "Piszkozat",
        '{{ _("Piszkozat") }}',
        1,
    ),
    (
        "Aktív",
        '{{ _("Aktív") }}',
        1,
    ),
    (
        "Lezárt",
        '{{ _("Lezárt") }}',
        1,
    ),
    (
        "<dt>Feladatok száma</dt>",
        '<dt>{{ _("Feladatok száma") }}</dt>',
        1,
    ),
    (
        "Helyes",
        '{{ _("Helyes") }}',
        1,
    ),
]

for old, new, expected in detail_lines:
    detail = replace_line(
        detail,
        old,
        new,
        expected,
        "detail",
    )


# Both close confirmations.
detail = replace_exact(
    detail,
    """onsubmit="return confirm(
            'Biztosan végleg lezárod ezt a feladatsort?'
        );\"""",
    """onsubmit='return confirm({{
            _("Biztosan végleg lezárod ezt a feladatsort?")
            | tojson
        }});'""",
    expected=2,
    label="detail confirm",
)


# Question heading: "<number>. feladat"
detail = replace_exact(
    detail,
    """{{ generated_question.display_position }}.
                feladat""",
    """{{
                _(
                    "%(position)s. feladat",
                    position=generated_question.display_position
                )
            }}""",
    label="detail question heading",
)


# Question metadata.
detail = replace_exact(
    detail,
    """Eredeti feladat-ID:
                {{ generated_question.question.id }}

                · Nehézség:
                {{ generated_question.question.difficulty }}""",
    """{{
                _(
                    "Eredeti feladat-ID: %(id)s · Nehézség: %(difficulty)s",
                    id=generated_question.question.id,
                    difficulty=generated_question.question.difficulty
                )
            }}""",
    label="detail metadata",
)


detail = replace_exact(
    detail,
    """A generált feladatsor nem
                tartalmaz kérdést.""",
    """{{ _("A generált feladatsor nem tartalmaz kérdést.") }}""",
    label="detail empty",
)


# ============================================================
# WRITE ONLY AFTER EVERY CHECK SUCCEEDED
# ============================================================

ROUTE.write_text(route, encoding="utf-8")
LIST.write_text(list_text, encoding="utf-8")
DETAIL.write_text(detail, encoding="utf-8")

print(f"UPDATED: {ROUTE}")
print(f"UPDATED: {LIST}")
print(f"UPDATED: {DETAIL}")
print("OK: generated test administration localized")
