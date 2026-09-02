#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/opt/feladatverseny"
ENV_FILE="$PROJECT_DIR/.env"

BACKUP_ROOT="/backup/feladatverseny"

TIMESTAMP="$(
    date '+%Y-%m-%d_%H-%M-%S'
)"

BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Environment file not found:"
    echo "$ENV_FILE"
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${DB_HOST:?DB_HOST is not set}"
: "${DB_PORT:?DB_PORT is not set}"
: "${DB_NAME:?DB_NAME is not set}"
: "${DB_USER:?DB_USER is not set}"
: "${DB_PASSWORD:?DB_PASSWORD is not set}"

mkdir -p "$BACKUP_DIR"

echo "========================================"
echo " Feladatverseny backup"
echo "========================================"
echo
echo "Started:"
date
echo
echo "Destination:"
echo "$BACKUP_DIR"

echo
echo "===== DATABASE ====="

PGPASSWORD="$DB_PASSWORD" \
pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=custom \
    --file="$BACKUP_DIR/database.dump"

echo "Database backup completed."

echo
echo "===== APPLICATION FILES ====="

tar \
    --exclude="$PROJECT_DIR/venv" \
    --exclude="$PROJECT_DIR/.git" \
    --exclude='*/__pycache__' \
    --exclude='*.pyc' \
    -czf "$BACKUP_DIR/application.tar.gz" \
    -C /opt \
    feladatverseny

echo "Application backup completed."

echo
echo "===== BACKUP INFO ====="

cat > "$BACKUP_DIR/backup-info.txt" <<EOF
Application: feladatverseny
Created: $(date --iso-8601=seconds)
Host: $(hostname)
Database: $DB_NAME
Database host: $DB_HOST
Database port: $DB_PORT
EOF

echo
echo "===== RETENTION ====="
echo "Deleting backups older than 72 hours."

find "$BACKUP_ROOT" \
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -mmin +4320 \
    -print \
    -exec rm -rf -- {} +

find "$BACKUP_ROOT" \
    -maxdepth 1 \
    -type f \
    -name 'feladatverseny-*.tar.gz' \
    -mmin +4320 \
    -print \
    -delete

echo
echo "===== RESULT ====="

du -sh "$BACKUP_DIR"

echo
echo "Backup completed:"
date
