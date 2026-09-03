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
        '"Nem választottál ki CSV-fájlt."',
        '_("Nem választottál ki CSV-fájlt.")',
        1,
    ),
    (
        '"Csak CSV-fájl tölthető fel."',
        '_("Csak CSV-fájl tölthető fel.")',
        1,
    ),
    (
        (
            '"A CSV nem olvasható "\n'
            '                    "UTF-8 kódolással."'
        ),
        (
            '_(\n'
            '                    "A CSV nem olvasható "\n'
            '                    "UTF-8 kódolással."\n'
            '                )'
        ),
        1,
    ),
    (
        '"A CSV fejlécének formátuma hibás."',
        '_("A CSV fejlécének formátuma hibás.")',
        1,
    ),
    (
        (
            '"Elvárt fejléc: "\n'
            '                                + ";".join(\n'
            '                                    CSV_FIELDNAMES\n'
            '                                )'
        ),
        (
            '_(\n'
            '                                "Elvárt fejléc: %(header)s",\n'
            '                                header=";".join(\n'
            '                                    CSV_FIELDNAMES\n'
            '                                ),\n'
            '                            )'
        ),
        1,
    ),
    (
        '"A forrásév nem érvényes szám."',
        '_("A forrásév nem érvényes szám.")',
        1,
    ),
    (
        '"A sorszám nem érvényes szám."',
        '_("A sorszám nem érvényes szám.")',
        1,
    ),
    (
        '"A nehézség nem érvényes szám."',
        '_("A nehézség nem érvényes szám.")',
        1,
    ),
    (
        (
            '"A helyes válasz "\n'
            '                        "nem érvényes szám."'
        ),
        (
            '_(\n'
            '                        "A helyes válasz "\n'
            '                        "nem érvényes szám."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"A forrásév nincs rögzítve: "\n'
            '                        f"{source_year_number}."'
        ),
        (
            '_(\n'
            '                        "A forrásév nincs rögzítve: "\n'
            '                        "%(year)s.",\n'
            '                        year=source_year_number,\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"A sorszám 1 és 25 "\n'
            '                        "közötti lehet."'
        ),
        (
            '_(\n'
            '                        "A sorszám 1 és 25 "\n'
            '                        "közötti lehet."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"A nehézség 1 és 25 "\n'
            '                        "közötti lehet."'
        ),
        (
            '_(\n'
            '                        "A nehézség 1 és 25 "\n'
            '                        "közötti lehet."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"A helyes válasz 1 és 5 "\n'
            '                        "közötti lehet."'
        ),
        (
            '_(\n'
            '                        "A helyes válasz 1 és 5 "\n'
            '                        "közötti lehet."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"Érvénytelen évfolyam: "\n'
            '                            f"{grade_value}."'
        ),
        (
            '_(\n'
            '                            "Érvénytelen évfolyam: "\n'
            '                            "%(grade)s.",\n'
            '                            grade=grade_value,\n'
            '                        )'
        ),
        1,
    ),
    (
        (
            '"Nem létező évfolyam: "\n'
            '                            f"{grade_number}."'
        ),
        (
            '_(\n'
            '                            "Nem létező évfolyam: "\n'
            '                            "%(grade)s.",\n'
            '                            grade=grade_number,\n'
            '                        )'
        ),
        1,
    ),
    (
        (
            '"Legalább egy évfolyam "\n'
            '                        "szükséges."'
        ),
        (
            '_(\n'
            '                        "Legalább egy évfolyam "\n'
            '                        "szükséges."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"Nem létező témakör: "\n'
            '                            f"{topic_value}."'
        ),
        (
            '_(\n'
            '                            "Nem létező témakör: "\n'
            '                            "%(topic)s.",\n'
            '                            topic=topic_value,\n'
            '                        )'
        ),
        1,
    ),
    (
        (
            '"Legalább egy témakör "\n'
            '                        "szükséges."'
        ),
        (
            '_(\n'
            '                        "Legalább egy témakör "\n'
            '                        "szükséges."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"A feladat valószínűleg már "\n'
            '                            "létezik az adatbázisban. "\n'
            '                            f"Feladat ID: {existing_question_id}."'
        ),
        (
            '_(\n'
            '                            "A feladat valószínűleg már "\n'
            '                            "létezik az adatbázisban. "\n'
            '                            "Feladat ID: %(question_id)s.",\n'
            '                            question_id=existing_question_id,\n'
            '                        )'
        ),
        1,
    ),
    (
        (
            '"Ugyanez a feladat már korábban "\n'
            '                            "szerepelt ebben a CSV-fájlban."'
        ),
        (
            '_(\n'
            '                            "Ugyanez a feladat már korábban "\n'
            '                            "szerepelt ebben a CSV-fájlban."\n'
            '                        )'
        ),
        1,
    ),
    (
        (
            '"Mind az öt "\n'
            '                        "válaszlehetőséget "\n'
            '                        "ki kell tölteni."'
        ),
        (
            '_(\n'
            '                        "Mind az öt "\n'
            '                        "válaszlehetőséget "\n'
            '                        "ki kell tölteni."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            '"Az aktív mező értéke "\n'
            '                        "legyen igen vagy nem."'
        ),
        (
            '_(\n'
            '                        "Az aktív mező értéke "\n'
            '                        "legyen igen vagy nem."\n'
            '                    )'
        ),
        1,
    ),
    (
        '"A CSV nem tartalmaz adatsort."',
        '_("A CSV nem tartalmaz adatsort.")',
        1,
    ),
    (
        (
            'f"{len(import_errors)} hibás "\n'
            '                    "CSV-sor található. "\n'
            '                    "Az import nem történt meg."'
        ),
        (
            '_(\n'
            '                    "%(count)s hibás CSV-sor található. "\n'
            '                    "Az import nem történt meg.",\n'
            '                    count=len(import_errors),\n'
            '                )'
        ),
        1,
    ),
    (
        (
            '"Hiba történt a "\n'
            '                        "CSV-import során."'
        ),
        (
            '"CSV import failed."'
        ),
        1,
    ),
    (
        (
            '"Az importálás közben "\n'
            '                        "hiba történt. Egyetlen "\n'
            '                        "rekordot sem mentettünk el."'
        ),
        (
            '_(\n'
            '                        "Az importálás közben "\n'
            '                        "hiba történt. Egyetlen "\n'
            '                        "rekordot sem mentettünk el."\n'
            '                    )'
        ),
        1,
    ),
    (
        (
            'f"{len(preview_rows)} sor "\n'
            '                    "ellenőrzése sikeres. "\n'
            '                    "Az adatok még nem kerültek "\n'
            '                    "az adatbázisba."'
        ),
        (
            '_(\n'
            '                    "%(count)s sor ellenőrzése sikeres. "\n'
            '                    "Az adatok még nem kerültek "\n'
            '                    "az adatbázisba.",\n'
            '                    count=len(preview_rows),\n'
            '                )'
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
    "OK: CSV import backend localized"
)
