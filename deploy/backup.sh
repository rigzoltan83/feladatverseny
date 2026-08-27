#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/feladatverseny"
DATA_DIR="/srv/feladatverseny"
BACKUP_ROOT="/backup/feladatverseny"
ENV_FILE="$PROJECT_DIR/.env"

RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Missing environment file: $ENV_FILE" >&2
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
WORK_DIR="$BACKUP_ROOT/.tmp-$TIMESTAMP"
ARCHIVE="$BACKUP_ROOT/feladatverseny-$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_ROOT"
mkdir -p "$WORK_DIR"

cleanup() {
    rm -rf "$WORK_DIR"
}

trap cleanup EXIT

echo "Backing up PostgreSQL database..."

PGPASSWORD="$DB_PASSWORD" \
pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=custom \
    --no-owner \
    --no-privileges \
    --file="$WORK_DIR/database.dump"

echo "Backing up media..."

if [ -d "$MEDIA_ROOT" ]; then
    tar -czf \
        "$WORK_DIR/media.tar.gz" \
        -C "$MEDIA_ROOT" \
        .
else
    tar -czf \
        "$WORK_DIR/media.tar.gz" \
        --files-from /dev/null
fi

echo "Backing up local configuration..."

cp \
    "$ENV_FILE" \
    "$WORK_DIR/environment.env"

chmod 600 \
    "$WORK_DIR/environment.env"

cat > "$WORK_DIR/backup-info.txt" <<INFO
Application: Feladatverseny
Created: $(date --iso-8601=seconds)
Database: $DB_NAME
Database host: $DB_HOST
Media root: $MEDIA_ROOT
INFO

tar -czf \
    "$ARCHIVE" \
    -C "$WORK_DIR" \
    .

chmod 600 "$ARCHIVE"

echo "Verifying backup archive..."

tar -tzf "$ARCHIVE" >/dev/null

echo "Removing backups older than $RETENTION_DAYS days..."

find "$BACKUP_ROOT" \
    -maxdepth 1 \
    -type f \
    -name 'feladatverseny-*.tar.gz' \
    -mtime "+$RETENTION_DAYS" \
    -delete

echo "Backup complete:"
echo "$ARCHIVE"
