#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/opt/feladatverseny"

cd "$PROJECT_DIR"

echo "===== ALEMBIC CURRENT ====="

CURRENT="$(
    ./venv/bin/flask db current 2>/dev/null \
        | tail -n 1 \
        | sed 's/ (head)//'
)"

echo "$CURRENT"

echo
echo "===== ALEMBIC HEAD ====="

HEAD="$(
    ./venv/bin/flask db heads 2>/dev/null \
        | tail -n 1 \
        | sed 's/ (head)//'
)"

echo "$HEAD"

if [[ "$CURRENT" != "$HEAD" ]]; then
    echo
    echo "FAIL: database migration is not at head"
    exit 1
fi

echo
echo "PASS: database migration is at head"

echo
echo "===== APPLICATION TESTS ====="

PYTHONPATH="$PROJECT_DIR" \
./venv/bin/python \
    scripts/full-test.py
