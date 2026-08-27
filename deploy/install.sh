#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/feladatverseny"
DATA_DIR="/srv/feladatverseny"
SERVICE_NAME="feladatverseny"

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer as root."
    exit 1
fi

echo "=== Feladatverseny installation ==="

if ! getent group feladat >/dev/null; then
    groupadd --system feladat
fi

if ! id feladatweb >/dev/null 2>&1; then
    useradd \
        --system \
        --gid feladat \
        --home-dir "$DATA_DIR" \
        --shell /usr/sbin/nologin \
        feladatweb
fi

mkdir -p \
    "$DATA_DIR/media" \
    "$DATA_DIR/backups"

chown -R feladatweb:feladat "$DATA_DIR"

if [ ! -d "$PROJECT_DIR/venv" ]; then
    python3 -m venv "$PROJECT_DIR/venv"
fi

"$PROJECT_DIR/venv/bin/pip" install \
    --upgrade pip

"$PROJECT_DIR/venv/bin/pip" install \
    -r "$PROJECT_DIR/requirements.txt"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp \
        "$PROJECT_DIR/.env.example" \
        "$PROJECT_DIR/.env"

    chmod 640 "$PROJECT_DIR/.env"

    echo
    echo "Created:"
    echo "  $PROJECT_DIR/.env"
    echo
    echo "Edit SECRET_KEY and database settings before starting."
fi

cp \
    "$PROJECT_DIR/deploy/feladatverseny.service" \
    /etc/systemd/system/feladatverseny.service

systemctl daemon-reload

echo
echo "Base installation complete."
echo
echo "Next:"
echo "  1. Edit $PROJECT_DIR/.env"
echo "  2. Create PostgreSQL database/user"
echo "  3. Run database migrations"
echo "  4. Enable and start $SERVICE_NAME"
