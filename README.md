# Feladatverseny

Flask/PostgreSQL web application for managing and running the Feladatverseny question competition.

## Requirements

- Ubuntu Linux
- Python 3
- PostgreSQL
- Git
- systemd

## Clone

    cd /opt
    sudo git clone https://github.com/rigzoltan83/feladatverseny.git
    cd /opt/feladatverseny

## Initial installation

    sudo /opt/feladatverseny/deploy/install.sh

The installer creates:

- `feladatweb` system user
- `feladat` system group
- `/srv/feladatverseny/media`
- `/srv/feladatverseny/backups`
- Python virtual environment
- systemd service
- `.env` from `.env.example`

## Configuration

Edit:

    sudo nano /opt/feladatverseny/.env

Configure at least:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `APP_BIND`

Generate a secret key with:

    python3 -c 'import secrets; print(secrets.token_hex(32))'

## PostgreSQL example

    CREATE USER feladatverseny_user
    WITH PASSWORD 'CHANGE_ME';

    CREATE DATABASE feladatverseny
    OWNER feladatverseny_user;

## Database migration

    cd /opt/feladatverseny
    source /opt/feladatverseny/venv/bin/activate
    flask --app run.py db upgrade
    flask --app run.py db current

## Start

    sudo systemctl enable --now feladatverseny
    sudo systemctl status feladatverseny --no-pager

## Health check

The application exposes `/health`.

Example:

    curl http://127.0.0.1:8000/health

Use the port configured in `APP_BIND`.

## Updating

    cd /opt/feladatverseny
    git pull
    source /opt/feladatverseny/venv/bin/activate
    pip install -r requirements.txt
    flask --app run.py db upgrade
    sudo systemctl restart feladatverseny

## Persistent data

Application source:

    /opt/feladatverseny

Persistent media:

    /srv/feladatverseny/media

Local configuration and secrets:

    /opt/feladatverseny/.env

The `.env` file is intentionally excluded from Git.
