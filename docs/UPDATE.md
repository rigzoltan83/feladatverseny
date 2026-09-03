# Updating Feladatverseny

This guide describes how to update an existing Feladatverseny installation.

## 1. Create a backup

Before updating, create a fresh backup:

    sudo systemctl start feladatverseny-backup.service

Verify that it completed successfully:

    sudo systemctl status \
      feladatverseny-backup.service \
      --no-pager -l

## 2. Update the source

Run Git operations as the repository owner, not as root:

    cd /opt/feladatverseny
    git pull

## 3. Update Python dependencies

    /opt/feladatverseny/venv/bin/pip install \
      -r /opt/feladatverseny/requirements.txt

## 4. Apply database migrations

    sudo \
      -u feladatweb \
      -g feladat \
      bash -c '
        set -a
        source /opt/feladatverseny/.env
        set +a

        cd /opt/feladatverseny

        /opt/feladatverseny/venv/bin/flask \
          --app run.py \
          db upgrade
      '

## 5. Restart the application

    sudo systemctl restart \
      feladatverseny.service

## 6. Verify the deployment

    sudo systemctl is-active \
      feladatverseny.service

Check the health endpoint using the configured local application port:

    curl http://127.0.0.1:5080/health

A healthy installation reports both the application and database
status as `ok`.
