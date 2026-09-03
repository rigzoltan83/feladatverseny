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
