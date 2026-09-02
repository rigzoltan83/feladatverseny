#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/feladatverseny"
DATA_DIR="/srv/feladatverseny"
MEDIA_DIR="$DATA_DIR/media"
BACKUP_DIR="/backup/feladatverseny"

SERVICE_NAME="feladatverseny"

DB_NAME="feladatverseny"
DB_USER="feladatverseny_user"
DB_HOST="127.0.0.1"
DB_PORT="5432"

APP_PORT="${APP_PORT:-8000}"
APP_BIND="127.0.0.1:${APP_PORT}"

APPLICATION_PREFIX="${APPLICATION_PREFIX:-}"

if [ -n "$APPLICATION_PREFIX" ]; then
    APPLICATION_PREFIX="/${APPLICATION_PREFIX#/}"
    APPLICATION_PREFIX="${APPLICATION_PREFIX%/}"
fi

ENV_FILE="$PROJECT_DIR/.env"

SEED_FILE=(
    "$PROJECT_DIR/deploy/seed/"
    "initial-data.sql.gz"
)

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer as root."
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project directory not found:"
    echo "$PROJECT_DIR"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "requirements.txt not found."
    exit 1
fi

if [ ! -f "$SEED_FILE" ]; then
    echo "Initial data seed not found:"
    echo "$SEED_FILE"
    exit 1
fi

echo
echo "========================================"
echo " Feladatverseny installation"
echo "========================================"
echo
echo "Project:  $PROJECT_DIR"
echo "Database: $DB_NAME"
echo "Bind:     $APP_BIND"
echo "Prefix:   ${APPLICATION_PREFIX:-/}"
echo "Backup:   $BACKUP_DIR"
echo

echo "===== 1. SYSTEM PACKAGES ====="

apt-get update

DEBIAN_FRONTEND=noninteractive \
apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    libpq-dev \
    postgresql \
    postgresql-client \
    git \
    curl

systemctl enable --now postgresql

echo
echo "===== 2. SYSTEM USER / DIRECTORIES ====="

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
    "$DATA_DIR" \
    "$MEDIA_DIR" \
    "$BACKUP_DIR"

chown \
    feladatweb:feladat \
    "$DATA_DIR" \
    "$MEDIA_DIR"

chmod 750 \
    "$DATA_DIR" \
    "$MEDIA_DIR"

chown root:root \
    "$BACKUP_DIR"

chmod 700 \
    "$BACKUP_DIR"

echo
echo "===== 3. PORT CHECK ====="

if ss -ltn \
    | awk '{print $4}' \
    | grep -Eq "[:.]${APP_PORT}$"
then
    echo
    echo "ERROR:"
    echo "TCP port $APP_PORT is already in use."
    echo
    echo "Run installer with another port:"
    echo
    echo "  sudo APP_PORT=5080 \\"
    echo "    $PROJECT_DIR/deploy/install.sh"
    echo
    exit 1
fi

echo "Port $APP_PORT is free."

echo
echo "===== 4. PYTHON ENVIRONMENT ====="

if [ ! -d "$PROJECT_DIR/venv" ]; then
    python3 -m venv \
        "$PROJECT_DIR/venv"
fi

"$PROJECT_DIR/venv/bin/python" \
    -m pip install \
    --upgrade pip

"$PROJECT_DIR/venv/bin/pip" \
    install \
    -r "$PROJECT_DIR/requirements.txt"

echo
echo "===== 5. DATABASE SAFETY CHECK ====="

DB_EXISTS="$(
    sudo -u postgres \
    psql \
        -Atqc \
        "SELECT 1
         FROM pg_database
         WHERE datname = '$DB_NAME';"
)"

if [ "$DB_EXISTS" = "1" ]; then
    echo
    echo "ERROR:"
    echo "Database '$DB_NAME' already exists."
    echo
    echo "Installer refuses to overwrite it."
    exit 1
fi

echo "Database name is free."

echo
echo "===== 6. DATABASE CREDENTIALS ====="

DB_PASSWORD="$(
    python3 -c \
    'import secrets; print(secrets.token_hex(24))'
)"

SECRET_KEY="$(
    python3 -c \
    'import secrets; print(secrets.token_hex(32))'
)"

echo
echo "===== 7. POSTGRESQL ROLE ====="

ROLE_EXISTS="$(
    sudo -u postgres \
    psql \
        -Atqc \
        "SELECT 1
         FROM pg_roles
         WHERE rolname = '$DB_USER';"
)"

if [ "$ROLE_EXISTS" = "1" ]; then
    echo "Role $DB_USER already exists."
    echo "Updating its password."

    sudo -u postgres \
    psql \
        --set=ON_ERROR_STOP=1 \
        --set=db_password="$DB_PASSWORD" \
        -c "
ALTER ROLE $DB_USER
WITH
    LOGIN
    PASSWORD :'db_password';
"
else
    sudo -u postgres \
    psql \
        --set=ON_ERROR_STOP=1 \
        --set=db_password="$DB_PASSWORD" \
        -c "
CREATE ROLE $DB_USER
WITH
    LOGIN
    PASSWORD :'db_password';
"
fi

echo
echo "===== 8. POSTGRESQL DATABASE ====="

sudo -u postgres \
createdb \
    --owner="$DB_USER" \
    "$DB_NAME"

echo
echo "===== 9. ENVIRONMENT FILE ====="

cat > "$ENV_FILE" <<EOF
APP_ENV=production

SECRET_KEY=$SECRET_KEY

DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

APP_TIMEZONE=Europe/Budapest
MEDIA_ROOT=$MEDIA_DIR

APP_BIND=$APP_BIND
APPLICATION_PREFIX=$APPLICATION_PREFIX
EOF

chown root:feladat \
    "$ENV_FILE"

chmod 640 \
    "$ENV_FILE"

echo "Environment created."

echo
echo "===== 10. DATABASE MIGRATIONS ====="

cd "$PROJECT_DIR"

set -a
source "$ENV_FILE"
set +a

"$PROJECT_DIR/venv/bin/flask" \
    --app run.py \
    db upgrade

echo
echo "===== 11. INITIAL DATA ====="

gzip -t "$SEED_FILE"

PGPASSWORD="$DB_PASSWORD" \
gunzip -c "$SEED_FILE" \
    | PGPASSWORD="$DB_PASSWORD" \
      psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --set=ON_ERROR_STOP=1

echo
echo "===== 12. SEQUENCE CHECK ====="

PGPASSWORD="$DB_PASSWORD" \
psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --set=ON_ERROR_STOP=1 \
    <<'SQL'

SELECT setval(
    pg_get_serial_sequence(
        'source_year',
        'id'
    ),
    COALESCE(
        (
            SELECT MAX(id)
            FROM source_year
        ),
        1
    ),
    EXISTS(
        SELECT 1
        FROM source_year
    )
);

SELECT setval(
    pg_get_serial_sequence(
        'question',
        'id'
    ),
    COALESCE(
        (
            SELECT MAX(id)
            FROM question
        ),
        1
    ),
    EXISTS(
        SELECT 1
        FROM question
    )
);

SELECT setval(
    pg_get_serial_sequence(
        'answer_option',
        'id'
    ),
    COALESCE(
        (
            SELECT MAX(id)
            FROM answer_option
        ),
        1
    ),
    EXISTS(
        SELECT 1
        FROM answer_option
    )
);

SELECT setval(
    pg_get_serial_sequence(
        'grade',
        'id'
    ),
    COALESCE(
        (
            SELECT MAX(id)
            FROM grade
        ),
        1
    ),
    EXISTS(
        SELECT 1
        FROM grade
    )
);

SELECT setval(
    pg_get_serial_sequence(
        'topic',
        'id'
    ),
    COALESCE(
        (
            SELECT MAX(id)
            FROM topic
        ),
        1
    ),
    EXISTS(
        SELECT 1
        FROM topic
    )
);

SELECT setval(
    pg_get_serial_sequence(
        'test_template',
        'id'
    ),
    COALESCE(
        (
            SELECT MAX(id)
            FROM test_template
        ),
        1
    ),
    EXISTS(
        SELECT 1
        FROM test_template
    )
);

SQL

echo
echo "===== 13. INITIAL DATA COUNTS ====="

PGPASSWORD="$DB_PASSWORD" \
psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -P pager=off \
    -c "
SELECT
    'source_year' AS table_name,
    COUNT(*) AS rows
FROM source_year

UNION ALL

SELECT
    'grade',
    COUNT(*)
FROM grade

UNION ALL

SELECT
    'topic',
    COUNT(*)
FROM topic

UNION ALL

SELECT
    'question',
    COUNT(*)
FROM question

UNION ALL

SELECT
    'answer_option',
    COUNT(*)
FROM answer_option

UNION ALL

SELECT
    'test_template',
    COUNT(*)
FROM test_template

ORDER BY table_name;
"

echo
echo "===== 14. FIRST ADMIN ====="
echo

read -r -p \
    "Admin username [admin]: " \
    ADMIN_USERNAME

ADMIN_USERNAME="${
    ADMIN_USERNAME:-admin
}"

read -r -p \
    "Admin full name [Administrator]: " \
    ADMIN_FULL_NAME

ADMIN_FULL_NAME="${
    ADMIN_FULL_NAME:-Administrator
}"

while true; do

    read -r -s -p \
        "Admin password: " \
        ADMIN_PASSWORD

    echo

    if [ "${#ADMIN_PASSWORD}" -lt 6 ]; then
        echo "Password must be at least 6 characters."
        continue
    fi

    read -r -s -p \
        "Repeat admin password: " \
        ADMIN_PASSWORD_CONFIRM

    echo

    if [ "$ADMIN_PASSWORD" != "$ADMIN_PASSWORD_CONFIRM" ]; then
        echo "Passwords do not match."
        continue
    fi

    break
done

ADMIN_HASH="$(
    "$PROJECT_DIR/venv/bin/python" \
        -c "
from werkzeug.security import generate_password_hash
import sys

print(
    generate_password_hash(
        sys.argv[1]
    )
)
" \
        "$ADMIN_PASSWORD"
)"

FIRST_GRADE_ID="$(
    PGPASSWORD="$DB_PASSWORD" \
    psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -Atqc "
SELECT id
FROM grade
ORDER BY grade_number, id
LIMIT 1;
"
)"

if [ -z "$FIRST_GRADE_ID" ]; then
    echo "No grade exists after seed import."
    exit 1
fi

PGPASSWORD="$DB_PASSWORD" \
psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --set=ON_ERROR_STOP=1 \
    --set=admin_username="$ADMIN_USERNAME" \
    --set=admin_full_name="$ADMIN_FULL_NAME" \
    --set=admin_hash="$ADMIN_HASH" \
    --set=grade_id="$FIRST_GRADE_ID" \
    -c "
INSERT INTO competitor (
    username,
    full_name,
    grade_id,
    password_hash,
    is_active,
    is_admin
)
VALUES (
    :'admin_username',
    :'admin_full_name',
    :'grade_id',
    :'admin_hash',
    TRUE,
    TRUE
);
"

unset ADMIN_PASSWORD
unset ADMIN_PASSWORD_CONFIRM
unset ADMIN_HASH

echo
echo "===== 15. APPLICATION SERVICE ====="

cp \
    "$PROJECT_DIR/deploy/feladatverseny.service" \
    /etc/systemd/system/feladatverseny.service

echo
echo "===== 16. BACKUP SERVICE ====="

cp \
    "$PROJECT_DIR/deploy/feladatverseny-backup.service" \
    /etc/systemd/system/feladatverseny-backup.service

cp \
    "$PROJECT_DIR/deploy/feladatverseny-backup.timer" \
    /etc/systemd/system/feladatverseny-backup.timer

systemctl daemon-reload

systemctl enable \
    feladatverseny-backup.timer

systemctl start \
    feladatverseny-backup.timer

echo
echo "===== 17. APPLICATION START ====="

systemctl enable \
    "$SERVICE_NAME"

systemctl restart \
    "$SERVICE_NAME"

sleep 3

echo
echo "===== 18. SERVICE STATUS ====="

systemctl status \
    "$SERVICE_NAME" \
    --no-pager

echo
echo "===== 19. HEALTH CHECK ====="

HEALTH_URL="http://127.0.0.1:${APP_PORT}/health"

for ATTEMPT in \
    1 2 3 4 5 6 7 8 9 10
do
    if curl \
        --fail \
        --silent \
        --show-error \
        "$HEALTH_URL" \
        >/dev/null
    then
        echo "Health check OK:"
        echo "$HEALTH_URL"
        break
    fi

    if [ "$ATTEMPT" = "10" ]; then
        echo
        echo "ERROR:"
        echo "Application health check failed."

        journalctl \
            -u "$SERVICE_NAME" \
            -n 100 \
            --no-pager

        exit 1
    fi

    sleep 2
done

echo
echo "===== 20. FIRST BACKUP ====="

"$PROJECT_DIR/deploy/backup.sh"

echo
echo "========================================"
echo " INSTALLATION COMPLETE"
echo "========================================"
echo
echo "Application:"
echo "  http://127.0.0.1:${APP_PORT}"
echo
echo "Admin:"
echo "  $ADMIN_USERNAME"
echo
echo "Database:"
echo "  $DB_NAME"
echo
echo "Backup:"
echo "  $BACKUP_DIR"
echo
echo "Service:"
echo "  systemctl status $SERVICE_NAME"
echo
echo "Backup timer:"
echo "  systemctl list-timers \\"
echo "    feladatverseny-backup.timer"
echo
