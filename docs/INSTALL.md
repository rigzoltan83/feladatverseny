# Installation Guide

This guide describes a standard Feladatverseny deployment on Ubuntu Linux.

## Requirements

Feladatverseny is designed for a Linux server with:

- Ubuntu Linux
- Python 3
- PostgreSQL
- Git
- systemd
- curl

The automated installer installs or configures the required application
components.

## Clone the repository

Run Git operations as a normal user rather than as root.

    cd /opt
    git clone https://github.com/rigzoltan83/feladatverseny.git
    cd /opt/feladatverseny

If `/opt` is not writable by the current user, prepare the project directory
with appropriate ownership before cloning.

## Standard installation

Run:

    sudo /opt/feladatverseny/deploy/install.sh

The installer automatically:

- creates the `feladatweb` system user
- creates the `feladat` system group
- creates persistent media storage
- creates the backup directory
- creates the Python virtual environment
- installs Python dependencies
- creates the PostgreSQL role
- creates the PostgreSQL database
- detects the local PostgreSQL port
- generates application secrets
- creates the local `.env` file
- applies database migrations
- imports the initial public seed
- creates the first administrator interactively
- installs the Gunicorn systemd service
- installs the backup service and timer
- starts the application
- performs a health check
- creates the first backup

## Application port

The application listens only on localhost by default.

The default bind address is based on the selected application port.

To use port `5080`:

    sudo APP_PORT=5080 /opt/feladatverseny/deploy/install.sh

This produces:

    APP_BIND=127.0.0.1:5080

## PostgreSQL port

The installer detects the local PostgreSQL server port automatically.

It can be overridden when required:

    sudo DB_PORT=5433 /opt/feladatverseny/deploy/install.sh

The installer verifies database authentication before applying migrations.

## Subpath deployment

Feladatverseny supports deployment below a URL prefix.

Example:

    sudo APP_PORT=5080 APPLICATION_PREFIX=/feladatverseny /opt/feladatverseny/deploy/install.sh

The generated configuration then contains:

    APP_BIND=127.0.0.1:5080
    APPLICATION_PREFIX=/feladatverseny

Generated Flask URLs, redirects and session cookie paths respect the
configured application prefix.

## Tailscale Serve example

For:

    APP_BIND=127.0.0.1:5080
    APPLICATION_PREFIX=/feladatverseny

publish the application to the tailnet with:

    sudo tailscale serve --bg --set-path /feladatverseny http://127.0.0.1:5080

Check the configuration with:

    sudo tailscale serve status

This allows Feladatverseny to remain bound to localhost instead of exposing
the Gunicorn service directly to the LAN.

## Configuration

The local configuration is stored in:

    /opt/feladatverseny/.env

Important settings include:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `APP_BIND`
- `APPLICATION_PREFIX`
- `MEDIA_ROOT`

The `.env` file contains secrets and must not be committed to Git.

## Persistent data

Default locations:

    Application:   /opt/feladatverseny
    Media:         /srv/feladatverseny/media
    Backups:       /backup/feladatverseny
    Configuration: /opt/feladatverseny/.env

## Application service

Check the service:

    sudo systemctl status feladatverseny.service --no-pager -l

Restart it:

    sudo systemctl restart feladatverseny.service

The production application is served by Gunicorn.

## Health check

The application exposes:

    /health

For an application running on port `5080`:

    curl http://127.0.0.1:5080/health

A healthy deployment reports both application and database status as `ok`.

## Database migrations

Migrations are applied automatically during installation.

For manual maintenance, run them using the application service environment:

    sudo -u feladatweb -g feladat bash -c 'set -a; source /opt/feladatverseny/.env; set +a; cd /opt/feladatverseny; /opt/feladatverseny/venv/bin/flask --app run.py db upgrade'

## Backups

Automated backups are installed as part of the standard deployment.

See:

- [Backup and recovery](BACKUP.md)

## Updating

For existing installations, see:

- [Updating Feladatverseny](UPDATE.md)

## Public installation data

The repository must contain only a sanitized public installation seed.

Production competitors, questions, tests, attempts, results, uploaded images
and other private data must never be distributed with the installer.

See:

- [Public release checklist](RELEASE.md)
