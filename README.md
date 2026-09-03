# Feladatverseny

Flask/PostgreSQL web application for managing and running the Feladatverseny question competition.

The application is designed for Ubuntu Linux and includes an automated installer, PostgreSQL database setup, systemd services, database migrations, initial seed data, administrator creation, health checks, and automated backups.

## Requirements

* Ubuntu Linux
* Python 3
* PostgreSQL
* Git
* systemd
* curl

The installer installs or configures the required application components.

## Clone

Clone the repository as a normal user rather than with `sudo`:

```bash
cd /opt

git clone \
  https://github.com/rigzoltan83/feladatverseny.git

cd /opt/feladatverseny
```

If `/opt` is not writable by the current user, create or prepare the project directory with appropriate permissions before cloning.

## Installation

For a standard installation:

```bash
cd /opt/feladatverseny

sudo \
  /opt/feladatverseny/deploy/install.sh
```

The installer automatically:

* creates the `feladatweb` system user
* creates the `feladat` system group
* creates `/srv/feladatverseny/media`
* creates `/backup/feladatverseny`
* creates the Python virtual environment
* installs Python dependencies
* creates the PostgreSQL role and database
* detects the local PostgreSQL server port
* generates the application secrets and database password
* creates `/opt/feladatverseny/.env`
* applies database migrations
* imports the initial seed data
* creates the first administrator account interactively
* installs and starts the Gunicorn systemd service
* installs and enables the backup timer
* performs an application health check
* creates the first backup

## Custom application port

The listening port can be selected during installation.

Example:

```bash
cd /opt/feladatverseny

sudo \
  APP_PORT=5080 \
  /opt/feladatverseny/deploy/install.sh
```

This results in:

```text
APP_BIND=127.0.0.1:5080
```

The application intentionally listens only on localhost by default.

## Subpath deployment

The application can be published below a URL prefix.

For example:

```bash
cd /opt/feladatverseny

sudo \
  APP_PORT=5080 \
  APPLICATION_PREFIX=/feladatverseny \
  /opt/feladatverseny/deploy/install.sh
```

This configuration is suitable for reverse proxies such as Tailscale Serve.

The generated environment contains:

```text
APP_BIND=127.0.0.1:5080
APPLICATION_PREFIX=/feladatverseny
```

Flask redirects, generated URLs, and the session cookie path respect the configured application prefix.

## Tailscale Serve example

For an application running on:

```text
127.0.0.1:5080
```

with:

```text
APPLICATION_PREFIX=/feladatverseny
```

it can be published on the tailnet with:

```bash
sudo tailscale serve \
  --bg \
  --set-path /feladatverseny \
  http://127.0.0.1:5080
```

Check the current Tailscale Serve configuration with:

```bash
sudo tailscale serve status
```

This adds the Feladatverseny path without requiring the application itself to listen on the LAN interface.

## Configuration

The generated local configuration is stored in:

```text
/opt/feladatverseny/.env
```

Important settings include:

* `SECRET_KEY`
* `DB_HOST`
* `DB_PORT`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`
* `APP_BIND`
* `APPLICATION_PREFIX`
* `MEDIA_ROOT`

The `.env` file contains secrets and is intentionally excluded from Git.

## PostgreSQL

The installer creates the PostgreSQL database and application role automatically.

The default names are:

```text
Database: feladatverseny
Role:     feladatverseny_user
```

The local PostgreSQL server port is detected automatically during installation.

It can be overridden when necessary:

```bash
sudo \
  DB_PORT=5433 \
  /opt/feladatverseny/deploy/install.sh
```

The installer verifies database authentication before continuing with migrations.

## Database migrations

Migrations are normally applied automatically during installation.

For manual maintenance:

```bash
cd /opt/feladatverseny

source \
  /opt/feladatverseny/venv/bin/activate

flask \
  --app run.py \
  db upgrade

flask \
  --app run.py \
  db current
```

## Application service

Check the application service:

```bash
sudo systemctl status \
  feladatverseny \
  --no-pager -l
```

Restart the application:

```bash
sudo systemctl restart \
  feladatverseny
```

The production service runs the application with Gunicorn.

## Health check

The application exposes:

```text
/health
```

For an installation using port `5080`:

```bash
curl \
  http://127.0.0.1:5080/health
```

A healthy installation reports application and database status as `ok`.

## Backups

The backup script is:

```text
/opt/feladatverseny/backup.sh
```

Backups are stored below:

```text
/backup/feladatverseny
```

Each backup contains:

* PostgreSQL database dump
* application files
* backup metadata

Python virtual environments, Git metadata, Python cache files, and compiled Python files are excluded from the application archive.

The backup timer runs every night at:

```text
00:10
```

Backups older than 72 hours are automatically removed.

Check the timer with:

```bash
sudo systemctl status \
  feladatverseny-backup.timer \
  --no-pager -l
```

Run a backup manually with:

```bash
sudo systemctl start \
  feladatverseny-backup.service
```

Check the result with:

```bash
sudo systemctl status \
  feladatverseny-backup.service \
  --no-pager -l
```

## Updating

Update the source as the repository owner:

```bash
cd /opt/feladatverseny

git pull
```

Update Python dependencies:

```bash
source \
  /opt/feladatverseny/venv/bin/activate

pip install \
  -r /opt/feladatverseny/requirements.txt
```

Apply database migrations:

```bash
cd /opt/feladatverseny

flask \
  --app run.py \
  db upgrade
```

Restart the service:

```bash
sudo systemctl restart \
  feladatverseny
```

Verify the service and health endpoint after updating.

## Persistent data

Application source:

```text
/opt/feladatverseny
```

Persistent media:

```text
/srv/feladatverseny/media
```

Backups:

```text
/backup/feladatverseny
```

Local configuration and secrets:

```text
/opt/feladatverseny/.env
```

## Tested deployment

The installation workflow has been tested with:

```text
APP_BIND=127.0.0.1:5080
APPLICATION_PREFIX=/feladatverseny
```

and Tailscale Serve publishing the application below `/feladatverseny`.

The tested deployment includes PostgreSQL authentication, migrations, initial seed import, administrator creation, Gunicorn/systemd startup, prefixed redirects, scoped session cookies, health checks, and automated backups.
