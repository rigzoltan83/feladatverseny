#!/usr/bin/env python3

from pathlib import Path


PATH = Path(
    "/opt/feladatverseny/"
    "app/routes/admin_templates.py"
)

text = PATH.read_text(
    encoding="utf-8"
)


def replace_exact(
    old,
    new,
    expected,
):
    global text

    count = text.count(old)

    if count != expected:
        raise RuntimeError(
            f"Expected {expected}, "
            f"found {count}: "
            f"{old!r}"
        )

    text = text.replace(
        old,
        new,
    )


# Flask-Babel import
replace_exact(
    """from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
""",
    """from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_babel import gettext as _
""",
    1,
)


replacements = [
    (
        '"A tesztsablon neve kötelező."',
        '_("A tesztsablon neve kötelező.")',
        2,
    ),

    (
        (
            '"Már létezik ilyen nevű "\n'
            '                    "tesztsablon."'
        ),
        (
            '_(\n'
            '                    "Már létezik ilyen nevű "\n'
            '                    "tesztsablon."\n'
            '                )'
        ),
        2,
    ),

    (
        (
            '"A feladatok száma "\n'
            '                    "1 és 100 közötti lehet."'
        ),
        (
            '_(\n'
            '                    "A feladatok száma "\n'
            '                    "1 és 100 közötti lehet."\n'
            '                )'
        ),
        2,
    ),

    (
        (
            '"Legalább egy évfolyamot "\n'
            '                    "ki kell választani."'
        ),
        (
            '_(\n'
            '                    "Legalább egy évfolyamot "\n'
            '                    "ki kell választani."\n'
            '                )'
        ),
        2,
    ),

    (
        (
            '"Legalább egy témakört "\n'
            '                    "ki kell választani."'
        ),
        (
            '_(\n'
            '                    "Legalább egy témakört "\n'
            '                    "ki kell választani."\n'
            '                )'
        ),
        2,
    ),

    (
        '"Az évfolyamválasztás érvénytelen."',
        '_("Az évfolyamválasztás érvénytelen.")',
        2,
    ),

    (
        '"A témakörválasztás érvénytelen."',
        '_("A témakörválasztás érvénytelen.")',
        2,
    ),

    (
        '"A tesztsablont létrehoztuk."',
        '_("A tesztsablont létrehoztuk.")',
        1,
    ),

    (
        (
            '"A tesztsablon módosításait "\n'
            '                    "elmentettük."'
        ),
        (
            '_(\n'
            '                    "A tesztsablon módosításait "\n'
            '                    "elmentettük."\n'
            '                )'
        ),
        1,
    ),

    (
        (
            'message = '
            '"A tesztsablont aktiváltuk."'
        ),
        (
            'message = _(\n'
            '            "A tesztsablont aktiváltuk."\n'
            '        )'
        ),
        1,
    ),

    (
        (
            'message = '
            '"A tesztsablont inaktiváltuk."'
        ),
        (
            'message = _(\n'
            '            "A tesztsablont inaktiváltuk."\n'
            '        )'
        ),
        1,
    ),
]


for old, new, expected in replacements:
    replace_exact(
        old,
        new,
        expected,
    )


PATH.write_text(
    text,
    encoding="utf-8",
)

print(
    "OK: test template backend localized"
)
