#!/usr/bin/env python3

from pathlib import Path


ROOT = Path("/opt/feladatverseny")


def replace_exact(
    relative_path: str,
    old: str,
    new: str,
) -> None:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")

    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"{relative_path}: expected exactly 1 match, "
            f"found {count} for:\n{old}"
        )

    path.write_text(
        text.replace(old, new, 1),
        encoding="utf-8",
    )

    print(f"OK: {relative_path}")


# ---------------------------------------------------------
# app/app.py
# Technical/internal strings -> English
# ---------------------------------------------------------

replace_exact(
    "app/app.py",
    '"""Környezeti változó lekérése egyértelmű hibaüzenettel."""',
    '"""Return a required environment variable with a clear error."""',
)

replace_exact(
    "app/app.py",
    'raise RuntimeError(f"Hiányzó kötelező környezeti változó: {name}")',
    'raise RuntimeError(f"Missing required environment variable: {name}")',
)

replace_exact(
    "app/app.py",
    '<html lang="hu">',
    '<html lang="en">',
)

replace_exact(
    "app/app.py",
    '<p class="status">A webalkalmazás működik.</p>',
    '<p class="status">The web application is running.</p>',
)

replace_exact(
    "app/app.py",
    """                Adatbázis-ellenőrzés:
                <a href="/health">/health</a>""",
    """                Database health check:
                <a href="/health">/health</a>""",
)

replace_exact(
    "app/app.py",
    'app.logger.exception("Adatbázis-kapcsolati hiba")',
    'app.logger.exception("Database connection error")',
)

replace_exact(
    "app/app.py",
    '"message": "Az adatbázis-kapcsolat nem érhető el.",',
    '"message": "The database connection is unavailable.",',
)


# ---------------------------------------------------------
# app/config.py
# ---------------------------------------------------------

replace_exact(
    "app/config.py",
    '"""Kötelező környezeti változó lekérése."""',
    '"""Return a required environment variable."""',
)

replace_exact(
    "app/config.py",
    'f"Hiányzó kötelező környezeti változó: {name}"',
    'f"Missing required environment variable: {name}"',
)


# ---------------------------------------------------------
# app/__init__.py
# Internal comments/docstrings/health messages -> English
# User-facing flash messages remain gettext Hungarian msgids.
# ---------------------------------------------------------

replace_exact(
    "app/__init__.py",
    '"""A Flask alkalmazás létrehozása."""',
    '"""Create and configure the Flask application."""',
)

replace_exact(
    "app/__init__.py",
    "# A Config csak a .env betöltése után importálható.",
    "# Config must be imported only after loading .env.",
)

replace_exact(
    "app/__init__.py",
    '"""Az első tesztútvonalak regisztrálása."""',
    '"""Register the application root and health routes."""',
)

replace_exact(
    "app/__init__.py",
    '''current_app.logger.exception(
                "Adatbázis-kapcsolati hiba"
            )''',
    '''current_app.logger.exception(
                "Database connection error"
            )''',
)

replace_exact(
    "app/__init__.py",
    '''"message": (
                        "Az adatbázis-kapcsolat "
                        "nem érhető el."
                    ),''',
    '''"message": (
                        "The database connection "
                        "is unavailable."
                    ),''',
)


# ---------------------------------------------------------
# app/routes/admin.py
# Developer comments -> English
# ---------------------------------------------------------

replace_exact(
    "app/routes/admin.py",
    "# Fontos: ez már a cikluson kívül van.",
    "# Important: this is intentionally outside the loop.",
)

replace_exact(
    "app/routes/admin.py",
    "# Fontos: ez már a for cikluson kívül van.",
    "# Important: this is intentionally outside the for loop.",
)


# ---------------------------------------------------------
# app/routes/admin_media.py
# User-facing messages -> gettext
# ---------------------------------------------------------

replace_exact(
    "app/routes/admin_media.py",
    '''from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    request,
    send_from_directory,
    url_for,
)''',
    '''from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    request,
    send_from_directory,
    url_for,
)
from flask_babel import gettext as _''',
)

replace_exact(
    "app/routes/admin_media.py",
    '''flash(
            "Nem választottál ki képfájlt.",
            "error",
        )''',
    '''flash(
            _("Nem választottál ki képfájlt."),
            "error",
        )''',
)

replace_exact(
    "app/routes/admin_media.py",
    '''flash(
            "Csak JPG vagy JPEG kép tölthető fel.",
            "error",
        )''',
    '''flash(
            _("Csak JPG vagy JPEG kép tölthető fel."),
            "error",
        )''',
)

replace_exact(
    "app/routes/admin_media.py",
    '''flash(
        f"A kép feltöltve: {question.image_filename}",
        "success",
    )''',
    '''flash(
        _(
            "A kép feltöltve: %(filename)s",
            filename=question.image_filename,
        ),
        "success",
    )''',
)

replace_exact(
    "app/routes/admin_media.py",
    '''flash(
            "A feladat képét töröltük.",
            "success",
        )''',
    '''flash(
            _("A feladat képét töröltük."),
            "success",
        )''',
)

replace_exact(
    "app/routes/admin_media.py",
    '''flash(
            "A feladathoz nem tartozik kép.",
            "error",
        )''',
    '''flash(
            _("A feladathoz nem tartozik kép."),
            "error",
        )''',
)

print()
print("SOURCE CLEANUP COMPLETE")
