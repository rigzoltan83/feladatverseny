#!/usr/bin/env python3

from pathlib import Path


PATH = Path(
    "/opt/feladatverseny/app/routes/admin.py"
)

text = PATH.read_text(
    encoding="utf-8"
)


def replace_exact(
    old,
    new,
    expected=1,
):
    global text

    count = text.count(old)

    if count != expected:
        raise RuntimeError(
            f"Expected {expected} occurrence(s), "
            f"found {count}: {old!r}"
        )

    text = text.replace(
        old,
        new,
    )


replacements = [
    (
        '"Érvényes forrásévet kell választani."',
        '_("Érvényes forrásévet kell választani.")',
        2,
    ),
    (
        '"A feladat sorszáma 1 és 25 közötti lehet."',
        '_("A feladat sorszáma 1 és 25 közötti lehet.")',
        2,
    ),
    (
        '"A nehézség 1 és 25 közötti lehet."',
        '_("A nehézség 1 és 25 közötti lehet.")',
        2,
    ),
    (
        '"A feladat szövege kötelező."',
        '_("A feladat szövege kötelező.")',
        3,
    ),
    (
        '"Legalább egy évfolyamot ki kell választani."',
        '_("Legalább egy évfolyamot ki kell választani.")',
        2,
    ),
    (
        '"Legalább egy témakört ki kell választani."',
        '_("Legalább egy témakört ki kell választani.")',
        2,
    ),
    (
        '"Mind az öt válaszlehetőséget ki kell tölteni."',
        '_("Mind az öt válaszlehetőséget ki kell tölteni.")',
        2,
    ),
    (
        '"Ki kell választani a helyes választ."',
        '_("Ki kell választani a helyes választ.")',
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
        (
            '"A feladatot és az öt "\n'
            '                    "válaszlehetőséget elmentettük."'
        ),
        (
            '_(\n'
            '                    "A feladatot és az öt "\n'
            '                    "válaszlehetőséget elmentettük."\n'
            '                )'
        ),
        1,
    ),
    (
        '"A feladat módosításait elmentettük."',
        '_("A feladat módosításait elmentettük.")',
        1,
    ),
    (
        'message = "A feladatot aktiváltuk."',
        'message = _("A feladatot aktiváltuk.")',
        1,
    ),
    (
        'message = "A feladatot inaktiváltuk."',
        'message = _("A feladatot inaktiváltuk.")',
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
    "OK: question CRUD backend messages localized"
)
