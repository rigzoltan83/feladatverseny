# Changelog

All notable changes to Feladatverseny will be documented in this file.

The project uses semantic versioning for public releases.

## Unreleased

No unreleased changes yet.

## 1.0.0 - 2026-09-03

### Added

- Hungarian and English user interface
- Competitor authentication and dashboard
- Question bank management
- Grade, topic and source-year reference data
- CSV question import
- Question image upload support
- Test template management
- Generated competition tests
- Competition lifecycle management
- Competitor submissions and scoring
- Detailed administrative results
- Automated Ubuntu installation
- PostgreSQL database setup and migrations
- Gunicorn systemd service
- Automated PostgreSQL and application backups
- Backup retention
- Health endpoint
- URL-prefix deployment support
- Tailscale Serve compatible deployment

### Security

- Backup directories and files are created with root-only
  permissions.
- Application secrets are excluded from Git.
