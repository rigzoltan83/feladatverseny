# Backup and Recovery

Feladatverseny includes an automated backup system based on a
systemd timer.

## Backup location

By default, backups are stored in:

    /backup/feladatverseny

Each timestamped backup directory contains:

- `database.dump` - PostgreSQL custom-format database dump
- `application.tar.gz` - application files and local configuration
- `backup-info.txt` - backup metadata

The application archive contains the local `.env` file and therefore
contains secrets.

Backup directories and files are created with root-only permissions.

## Schedule

The supplied systemd timer runs the backup every night at 00:10.

Check the timer:

    sudo systemctl status \
      feladatverseny-backup.timer \
      --no-pager -l

List scheduled runs:

    sudo systemctl list-timers \
      feladatverseny-backup.timer

## Manual backup

Create a backup immediately:

    sudo systemctl start \
      feladatverseny-backup.service

Check the result:

    sudo systemctl status \
      feladatverseny-backup.service \
      --no-pager -l

The backup service is a oneshot service. An `inactive (dead)` state
after a successful run is normal when the process exited with
`0/SUCCESS`.

## Retention

Backups older than 72 hours are automatically removed.

## Validation

Validate an application archive:

    sudo tar \
      -tzf \
      /backup/feladatverseny/TIMESTAMP/application.tar.gz

Validate a PostgreSQL dump:

    sudo pg_restore \
      --list \
      /backup/feladatverseny/TIMESTAMP/database.dump

## Security

Backups contain application configuration, database content and
application secrets.

Never publish backups or commit them to Git.

Do not copy backups to publicly accessible storage or weaken their
filesystem permissions without a specific reason.

## Recovery

Before restoring a production installation, preserve the current
installation and database.

A full restore procedure should be tested on a separate installation
before it is required for production recovery.
