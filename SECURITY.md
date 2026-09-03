# Security Policy

## Supported versions

Feladatverseny is currently in pre-release development.

Security fixes are applied to the latest version of the `main` branch.

After the first public release, supported versions will be documented here.

## Reporting a vulnerability

Please do not publish security vulnerabilities in public GitHub issues.

Instead, contact the project maintainer privately.

When reporting a vulnerability, include:

- affected version or commit
- affected component or endpoint
- steps required to reproduce the issue
- expected and actual behavior
- potential security impact
- any relevant logs or screenshots

Do not include real credentials, private user data or production database
content in vulnerability reports.

## Sensitive data

Feladatverseny installations may contain:

- user accounts
- competition questions
- submissions and results
- uploaded question images
- database credentials
- application secrets

The repository must not contain production credentials, private backups or
production user data.

Public installation seeds and screenshots must be sanitized before release.

## Backups

Application backups contain local configuration and database content.

Backup directories and files should remain accessible only to authorized
administrators and must never be committed to Git or published publicly.
