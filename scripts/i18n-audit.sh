#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/opt/feladatverseny"

cd "$PROJECT_DIR"

echo "========================================"
echo " FELADATVERSENY I18N AUDIT"
echo "========================================"

echo
echo "===== TEMPLATES: HUNGARIAN TEXT ====="

grep \
    -RIn \
    --include='*.html' \
    -E '[áéíóöőúüűÁÉÍÓÖŐÚÜŰ]' \
    app/templates \
    || true

echo
echo "===== PYTHON: HUNGARIAN TEXT ====="

grep \
    -RIn \
    --include='*.py' \
    -E '[áéíóöőúüűÁÉÍÓÖŐÚÜŰ]' \
    app \
    || true

echo
echo "===== GETTEXT MARKERS ====="

grep \
    -RIn \
    --include='*.py' \
    --include='*.html' \
    -E '(_\(|gettext\()' \
    app \
    || true

echo
echo "===== ENGLISH CATALOG EMPTY TRANSLATIONS ====="

python3 - <<'PYTHON'
from pathlib import Path

path = Path(
    "translations/en/LC_MESSAGES/messages.po"
)

msgid = None

for line in path.read_text(
    encoding="utf-8"
).splitlines():
    if line.startswith('msgid "'):
        msgid = line[7:-1]

    elif (
        line == 'msgstr ""'
        and msgid
    ):
        print(msgid)
PYTHON

echo
echo "===== GIT ====="

git status --short
