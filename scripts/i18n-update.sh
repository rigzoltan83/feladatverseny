#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/opt/feladatverseny"
PYBABEL="$PROJECT_DIR/venv/bin/pybabel"

cd "$PROJECT_DIR"

echo "===== EXTRACT ====="

"$PYBABEL" \
    extract \
    -F "$PROJECT_DIR/babel.cfg" \
    -o "$PROJECT_DIR/messages.pot" \
    "$PROJECT_DIR"

echo
echo "===== UPDATE HU ====="

"$PYBABEL" \
    update \
    -i "$PROJECT_DIR/messages.pot" \
    -d "$PROJECT_DIR/translations" \
    -l hu

echo
echo "===== UPDATE EN ====="

"$PYBABEL" \
    update \
    -i "$PROJECT_DIR/messages.pot" \
    -d "$PROJECT_DIR/translations" \
    -l en

echo
echo "===== COMPILE ====="

"$PYBABEL" \
    compile \
    -d "$PROJECT_DIR/translations"

echo
echo "===== DONE ====="
