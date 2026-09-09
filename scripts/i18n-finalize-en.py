#!/usr/bin/env python3

from pathlib import Path

from babel.messages.pofile import (
    read_po,
    write_po,
)


PO_PATH = Path(
    "/opt/feladatverseny/"
    "translations/en/LC_MESSAGES/messages.po"
)

TRANSLATIONS = {
    (
        "Kézi feladatválasztás csak manuális "
        "tesztsablonnál használható."
    ):
        (
            "Manual question selection is available "
            "only for manual test templates."
        ),

    "Legalább egy feladatot ki kell választani.":
        "At least one question must be selected.",

    "Legfeljebb 100 feladat választható ki.":
        "At most 100 questions can be selected.",

    (
        "A kiválasztott feladatok között "
        "érvénytelen vagy inaktív feladat "
        "található."
    ):
        (
            "The selected questions include an "
            "invalid or inactive question."
        ),

    (
        "A manuális feladatsor "
        "kiválasztását elmentettük."
    ):
        "The manual question selection has been saved.",

    "Automatikus":
        "Automatic",

    "Manuális":
        "Manual",

    "Manuális feladatsor":
        "Manual question set",

    "%(count)s feladat van kiválasztva.":
        "%(count)s questions selected.",

    "Kiválasztás módosítása":
        "Edit selection",

    "Meglévő feladatok kiválasztása":
        "Select existing questions",

    "Sorrend":
        "Order",

    (
        "Ehhez a manuális sablonhoz "
        "még nincs feladat kiválasztva."
    ):
        (
            "No questions have been selected for "
            "this manual template yet."
        ),

    "Feladatok kiválasztása":
        "Select questions",

    "Vissza a sablonhoz":
        "Back to template",

    "Kérdésbank szűrése":
        "Filter question bank",

    "Meglévő feladatok":
        "Existing questions",

    "%(count)s aktív feladat látható.":
        "%(count)s active questions shown.",

    "Kiválasztás mentése":
        "Save selection",

    "Kiválasztás":
        "Selection",

    (
        "A szűrésnek egyetlen "
        "aktív feladat sem felel meg."
    ):
        "No active questions match the filters.",

    "Az összeállítás módja érvénytelen.":
        "The composition mode is invalid.",
    "Összeállítás módja":
        "Composition mode",
    "Automatikus összeállítás":
        "Automatic composition",
    "Manuális összeállítás":
        "Manual composition",
    (
        "A rendszer az évfolyamok és "
        "témakörök alapján választ "
        "feladatokat."
    ):
        (
            "The system selects questions based on "
            "grades and topics."
        ),
    "A feladatsor kérdéseit kézzel állítod össze.":
        "You select the questions manually.",
    (
        "Automatikus összeállításnál ennyi "
        "feladatot választ a rendszer. "
        "Manuális összeállításnál ez a "
        "tervezett feladatszám."
    ):
        (
            "For automatic composition, the system "
            "selects this many questions. For manual "
            "composition, this is the planned number "
            "of questions."
        ),
    (
        "Automatikus összeállításnál kötelező. "
        "Manuális összeállításnál opcionális, "
        "és a kérdésbank szűrését segíti."
    ):
        (
            "Required for automatic composition. "
            "Optional for manual composition and "
            "used to help filter the question bank."
        ),
    (
        "Csak automatikus "
        "összeállításnál használható."
    ):
        (
            "Available only for automatic "
            "composition."
        ),

    "Leírás":
        "Description",

    "Igen":
        "Yes",

    "Nem":
        "No",

    "Feladatok száma":
        "Number of questions",

    "Nincs még rögzített tesztsablon.":
        "No test templates have been created yet.",

    "Nem választottál ki képfájlt.":
        "No image file was selected.",

    "Csak JPG vagy JPEG kép tölthető fel.":
        "Only JPG or JPEG images can be uploaded.",

    "A kép feltöltve: %(filename)s":
        "Image uploaded: %(filename)s",

    "A feladat képét töröltük.":
        "The question image was deleted.",

    "A feladathoz nem tartozik kép.":
        "This question does not have an image.",

    "Feladat képe – opcionális":
        "Question image – optional",

    "Feladat képe – opcionális csere":
        "Question image – optional replacement",

    "JPG vagy JPEG kép tölthető fel. "
    "Ha nem választasz képet, a feladat "
    "kép nélkül kerül mentésre.":
        "A JPG or JPEG image can be uploaded. "
        "If you do not select an image, the question "
        "will be saved without one.",

    "Töltsd ki mind az öt választ, majd jelöld meg "
    "az összes helyes választ.":
        "Fill in all five answers, then select "
        "all correct answers.",

    "Legalább egy érvényes helyes "
    "választ ki kell választani.":
        "At least one valid correct answer "
        "must be selected.",

    "Érvénytelen helyes "
    "válasz: %(answer)s.":
        "Invalid correct answer: %(answer)s.",

    "Legalább egy helyes "
    "választ meg kell adni.":
        "At least one correct answer "
        "must be provided.",

    "A helyes válaszok csak "
    "1 és 5 közöttiek lehetnek.":
        "Correct answers must be "
        "between 1 and 5.",

    "A témakör magyar neve kötelező.":
        "The Hungarian topic name is required.",

    "A témakör magyar neve "
    "legfeljebb 100 karakter lehet.":
        "The Hungarian topic name can be "
        "at most 100 characters.",

    "A témakör angol neve "
    "legfeljebb 100 karakter lehet.":
        "The English topic name can be "
        "at most 100 characters.",

    "Már létezik ilyen nevű "
    "témakör.":
        "A topic with this name already exists.",

    "A témakör sikeresen létrejött.":
        "Topic created successfully.",

    "Új témakör létrehozása":
        "Create new topic",

    "Magyar megnevezés":
        "Hungarian name",

    "Angol megnevezés":
        "English name",

    "Témakör létrehozása":
        "Create topic",

    "Rögzített témakörök":
        "Created topics",

    "Magyar név":
        "Hungarian name",

    "Angol név":
        "English name",

    "Témakör szerkesztése":
        "Edit topic",

    "A témakör módosításait elmentettük.":
        "Topic changes saved.",

    "A témakört aktiváltuk.":
        "Topic activated.",

    "A témakört inaktiváltuk.":
        "Topic deactivated.",

    "Aktív témakör":
        "Active topic",

    "Műveletek":
        "Actions",

    "Szerkesztés":
        "Edit",

    "Inaktiválás":
        "Deactivate",

    "Aktiválás":
        "Activate",

    "Mentés":
        "Save",

    "Adj meg egy magyar nevet, "
    "és opcionálisan az angol "
    "megnevezést is.":
        "Enter a Hungarian name and optionally "
        "the English name as well.",

    "Összesen":
        "Total",
}


with PO_PATH.open(
    "r",
    encoding="utf-8",
) as file_handle:
    catalog = read_po(file_handle)


found = set()

for message in catalog:
    if message.id not in TRANSLATIONS:
        continue

    message.string = TRANSLATIONS[message.id]
    message.flags.discard("fuzzy")

    found.add(message.id)

    print(
        f"{message.id!r} => "
        f"{message.string!r}"
    )


missing = set(TRANSLATIONS) - found

if missing:
    raise RuntimeError(
        "Missing message IDs:\n"
        + "\n".join(
            sorted(missing)
        )
    )


with PO_PATH.open(
    "wb",
) as file_handle:
    write_po(
        file_handle,
        catalog,
        width=79,
    )


print()
print(
    f"OK: {len(found)} English "
    "translations finalized"
)
