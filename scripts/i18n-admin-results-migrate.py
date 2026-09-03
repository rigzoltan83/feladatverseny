#!/usr/bin/env python3

from pathlib import Path
import re


ROOT = Path("/opt/feladatverseny")

ROUTE = ROOT / "app/routes/admin.py"
LIST = ROOT / "app/templates/admin/results.html"
DETAIL = ROOT / "app/templates/admin/result_detail.html"
ATTEMPT = ROOT / "app/templates/admin/attempt_result_detail.html"


def replace_exact(
    text,
    old,
    new,
    expected=1,
    label="",
):
    count = text.count(old)

    if count != expected:
        raise RuntimeError(
            f"{label}: expected {expected}, "
            f"found {count}: {old!r}"
        )

    return text.replace(old, new)


def replace_line(
    text,
    old,
    new,
    expected=1,
    label="",
):
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
        lambda match:
            match.group(1) + new,
        text,
    )


# ============================================================
# ROUTE
# ============================================================

route = ROUTE.read_text(
    encoding="utf-8"
)


# result_detail duration
route = replace_exact(
    route,
    '''            if hours:
                duration_text = (
                    f"{hours} óra "
                    f"{minutes} perc "
                    f"{seconds} mp"
                )
            elif minutes:
                duration_text = (
                    f"{minutes} perc "
                    f"{seconds} mp"
                )
            else:
                duration_text = (
                    f"{seconds} mp"
                )
''',
    '''            if hours:
                duration_text = _(
                    "%(hours)s h %(minutes)s min "
                    "%(seconds)s sec",
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                )
            elif minutes:
                duration_text = _(
                    "%(minutes)s min %(seconds)s sec",
                    minutes=minutes,
                    seconds=seconds,
                )
            else:
                duration_text = _(
                    "%(seconds)s sec",
                    seconds=seconds,
                )
''',
    label="result detail duration",
)


# attempt_result_detail duration
route = replace_exact(
    route,
    '''        if hours:
            duration_text = (
                f"{hours} óra "
                f"{minutes} perc "
                f"{seconds} mp"
            )
        elif minutes:
            duration_text = (
                f"{minutes} perc "
                f"{seconds} mp"
            )
        else:
            duration_text = f"{seconds} mp"
''',
    '''        if hours:
            duration_text = _(
                "%(hours)s h %(minutes)s min "
                "%(seconds)s sec",
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            )
        elif minutes:
            duration_text = _(
                "%(minutes)s min %(seconds)s sec",
                minutes=minutes,
                seconds=seconds,
            )
        else:
            duration_text = _(
                "%(seconds)s sec",
                seconds=seconds,
            )
''',
    label="attempt detail duration",
)


# Fix submitted_count so it is always initialized,
# including a round with zero attempts.
route = replace_exact(
    route,
    '''        submitted_count = sum(
            1
            for row in result_rows
            if row["attempt"].status == "submitted"
        )

    return render_template(
''',
    '''    submitted_count = sum(
        1
        for row in result_rows
        if row["attempt"].status == "submitted"
    )

    return render_template(
''',
    label="submitted count scope",
)


# ============================================================
# RESULTS LIST
# ============================================================

text = LIST.read_text(
    encoding="utf-8"
)

line_replacements = [
    (
        "Eredmények – Feladatverseny",
        '{{ _("Eredmények – Feladatverseny") }}',
        1,
    ),
    (
        "<h1>Eredmények</h1>",
        '<h1>{{ _("Eredmények") }}</h1>',
        1,
    ),
    (
        "Vissza az adminisztrációhoz",
        '{{ _("Vissza az adminisztrációhoz") }}',
        1,
    ),
    (
        "<th>Forduló</th>",
        '<th>{{ _("Forduló") }}</th>',
        1,
    ),
    (
        "Feladatok",
        '{{ _("Feladatok") }}',
        1,
    ),
    (
        "Résztvevők",
        '{{ _("Résztvevők") }}',
        1,
    ),
    (
        "Beadta",
        '{{ _("Beadta") }}',
        1,
    ),
    (
        "Átlag",
        '{{ _("Átlag") }}',
        1,
    ),
    (
        "Legjobb",
        '{{ _("Legjobb") }}',
        1,
    ),
    (
        "Művelet",
        '{{ _("Művelet") }}',
        1,
    ),
    (
        "Részletek",
        '{{ _("Részletek") }}',
        1,
    ),
    (
        "Még nincs lezárt forduló.",
        '{{ _("Még nincs lezárt forduló.") }}',
        1,
    ),
]

for old, new, expected in line_replacements:
    text = replace_line(
        text,
        old,
        new,
        expected,
        "results list",
    )

text = replace_exact(
    text,
    '''Lezárt fordulók és kitöltések.''',
    '''{{ _("Lezárt fordulók és kitöltések.") }}''',
    label="results description",
)

LIST.write_text(
    text,
    encoding="utf-8",
)


# ============================================================
# RESULT DETAIL
# ============================================================

text = DETAIL.read_text(
    encoding="utf-8"
)

line_replacements = [
    (
        "A lezárt forduló részletes eredményei.",
        '{{ _("A lezárt forduló részletes eredményei.") }}',
        1,
    ),
    (
        "Vissza az eredményekhez",
        '{{ _("Vissza az eredményekhez") }}',
        1,
    ),
    (
        "Feladatsor megtekintése",
        '{{ _("Feladatsor megtekintése") }}',
        1,
    ),
    (
        "<h2>Forduló adatai</h2>",
        '<h2>{{ _("Forduló adatai") }}</h2>',
        1,
    ),
    (
        "<dt>Feladatok</dt>",
        '<dt>{{ _("Feladatok") }}</dt>',
        1,
    ),
    (
        "<dt>Résztvevők</dt>",
        '<dt>{{ _("Résztvevők") }}</dt>',
        1,
    ),
    (
        "<dt>Beadta</dt>",
        '<dt>{{ _("Beadta") }}</dt>',
        1,
    ),
    (
        "<dt>Nem adta be</dt>",
        '<dt>{{ _("Nem adta be") }}</dt>',
        1,
    ),
    (
        "<h2>Versenyzői eredmények</h2>",
        '<h2>{{ _("Versenyzői eredmények") }}</h2>',
        1,
    ),
    (
        "Helyezés",
        '{{ _("Helyezés") }}',
        1,
    ),
    (
        "<th>Versenyző</th>",
        '<th>{{ _("Versenyző") }}</th>',
        1,
    ),
    (
        "Évfolyam",
        '{{ _("Évfolyam") }}',
        1,
    ),
    (
        "Pontszám",
        '{{ _("Pontszám") }}',
        1,
    ),
    (
        "Eredmény",
        '{{ _("Eredmény") }}',
        1,
    ),
    (
        "Állapot",
        '{{ _("Állapot") }}',
        1,
    ),
    (
        "Kezdés",
        '{{ _("Kezdés") }}',
        1,
    ),
    (
        "Beadás",
        '{{ _("Beadás") }}',
        1,
    ),
    (
        "Kitöltési idő",
        '{{ _("Kitöltési idő") }}',
        1,
    ),
    (
        "Művelet",
        '{{ _("Művelet") }}',
        1,
    ),
    (
        "Beadva",
        '{{ _("Beadva") }}',
        1,
    ),
    (
        "Nem adta be",
        '{{ _("Nem adta be") }}',
        1,
    ),
    (
        "Kitöltés",
        '{{ _("Kitöltés") }}',
        1,
    ),
]

for old, new, expected in line_replacements:
    text = replace_line(
        text,
        old,
        new,
        expected,
        "result detail",
    )

text = replace_exact(
    text,
    '''{{ generated_test.name }} – Eredmények''',
    '''{{ generated_test.name }} – {{ _("Eredmények") }}''',
    label="result title",
)

text = replace_exact(
    text,
    '''Ehhez a fordulóhoz nem tartozik
                egyetlen kitöltés sem.''',
    '''{{ _("Ehhez a fordulóhoz nem tartozik egyetlen kitöltés sem.") }}''',
    label="result empty",
)

DETAIL.write_text(
    text,
    encoding="utf-8",
)


# ============================================================
# ATTEMPT RESULT DETAIL
# ============================================================

text = ATTEMPT.read_text(
    encoding="utf-8"
)

line_replacements = [
    (
        "Vissza a forduló eredményeihez",
        '{{ _("Vissza a forduló eredményeihez") }}',
        1,
    ),
    (
        "<h2>Versenyző</h2>",
        '<h2>{{ _("Versenyző") }}</h2>',
        1,
    ),
    (
        "<dt>Név</dt>",
        '<dt>{{ _("Név") }}</dt>',
        1,
    ),
    (
        "<dt>Felhasználónév</dt>",
        '<dt>{{ _("Felhasználónév") }}</dt>',
        1,
    ),
    (
        "<dt>Évfolyam</dt>",
        '<dt>{{ _("Évfolyam") }}</dt>',
        1,
    ),
    (
        "<dt>Állapot</dt>",
        '<dt>{{ _("Állapot") }}</dt>',
        1,
    ),
    (
        "Beadva",
        '{{ _("Beadva") }}',
        1,
    ),
    (
        "Nem adta be",
        '{{ _("Nem adta be") }}',
        1,
    ),
    (
        "<h2>Eredmény</h2>",
        '<h2>{{ _("Eredmény") }}</h2>',
        1,
    ),
    (
        "<dt>Pontszám</dt>",
        '<dt>{{ _("Pontszám") }}</dt>',
        1,
    ),
    (
        "<dt>Százalék</dt>",
        '<dt>{{ _("Százalék") }}</dt>',
        1,
    ),
    (
        "<dt>Kezdés</dt>",
        '<dt>{{ _("Kezdés") }}</dt>',
        1,
    ),
    (
        "<dt>Beadás</dt>",
        '<dt>{{ _("Beadás") }}</dt>',
        1,
    ),
    (
        "<dt>Kitöltési idő</dt>",
        '<dt>{{ _("Kitöltési idő") }}</dt>',
        1,
    ),
    (
        "Nem válaszolt",
        '{{ _("Nem válaszolt") }}',
        1,
    ),
    (
        "Helyes",
        '{{ _("Helyes") }}',
        1,
    ),
    (
        "Hibás",
        '{{ _("Hibás") }}',
        1,
    ),
    (
        "✓ Ezt jelölte – helyes",
        '{{ _("✓ Ezt jelölte – helyes") }}',
        1,
    ),
    (
        "✗ Ezt jelölte",
        '{{ _("✗ Ezt jelölte") }}',
        1,
    ),
    (
        "✓ Helyes válasz",
        '{{ _("✓ Helyes válasz") }}',
        1,
    ),
    (
        "A feladatsor nem tartalmaz kérdést.",
        '{{ _("A feladatsor nem tartalmaz kérdést.") }}',
        1,
    ),
]

for old, new, expected in line_replacements:
    text = replace_line(
        text,
        old,
        new,
        expected,
        "attempt detail",
    )


text = replace_exact(
    text,
    '''{{ generated_test.name }}
                – részletes kitöltés''',
    '''{{
                _(
                    "%(test_name)s – részletes kitöltés",
                    test_name=generated_test.name
                )
            }}''',
    label="attempt subtitle",
)


text = replace_exact(
    text,
    '''{{
                        generated_question
                        .display_position
                    }}. feladat''',
    '''{{
                        _(
                            "%(position)s. feladat",
                            position=(
                                generated_question
                                .display_position
                            )
                        )
                    }}''',
    label="attempt question heading",
)

ATTEMPT.write_text(
    text,
    encoding="utf-8",
)


# ============================================================
# FINAL
# ============================================================

print(f"UPDATED: {ROUTE}")
print(f"UPDATED: {LIST}")
print(f"UPDATED: {DETAIL}")
print(f"UPDATED: {ATTEMPT}")

print(
    "OK: results administration localized"
)
