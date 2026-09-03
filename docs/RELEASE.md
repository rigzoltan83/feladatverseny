# Public Release Checklist

This checklist must be completed before publishing a public
Feladatverseny release.

## Code quality

- [ ] Python source compiles successfully
- [ ] All Jinja templates compile successfully
- [ ] `git diff --check` reports no errors
- [ ] Application service starts successfully
- [ ] `/health` reports application and database status as `ok`

## Localization

- [ ] Hungarian interface tested
- [ ] English interface tested
- [ ] English catalog contains no empty translations
- [ ] English catalog contains no fuzzy translations

## Installation

- [ ] Clean Ubuntu installation tested
- [ ] PostgreSQL database creation tested
- [ ] Database migrations tested
- [ ] Initial administrator creation tested
- [ ] systemd service installation tested
- [ ] Application-prefix deployment tested

## Backup

- [ ] Manual backup tested
- [ ] PostgreSQL dump validated with `pg_restore --list`
- [ ] Application archive validated with `tar -tzf`
- [ ] Backup directories are root-only
- [ ] Backup files are root-only
- [ ] Backup timer tested

## Public data sanitization - mandatory

The production database must never be modified merely to prepare a
public release.

The public installation seed must be generated and verified
separately.

Before release:

- [ ] Preserve a verified production backup
- [ ] Inspect every table included in the installation seed
- [ ] Remove real competitors and user accounts
- [ ] Remove real questions
- [ ] Remove answers and explanations belonging to real questions
- [ ] Remove test templates containing private competition data
- [ ] Remove generated tests and competition rounds
- [ ] Remove submissions and attempts
- [ ] Remove scores and results
- [ ] Remove uploaded question images
- [ ] Remove personal information
- [ ] Remove organization-specific private information
- [ ] Keep only reference data required for a clean installation
- [ ] Verify the sanitized seed programmatically
- [ ] Inspect the sanitized seed before publication
- [ ] Perform a completely clean installation using the public seed
- [ ] Verify that the clean installation contains no private data

The installer must create the first administrator interactively.

No real administrator credentials may be included in the repository.

## Repository security

- [ ] `.env` is not tracked
- [ ] Backups are not tracked
- [ ] Uploaded media is not tracked
- [ ] No credentials or secrets are present in published files
- [ ] Git history has been reviewed for accidentally committed secrets
- [ ] Public screenshots contain no private data

## Documentation

- [ ] README is current
- [ ] Installation documentation is current
- [ ] Update documentation is current
- [ ] Backup documentation is current
- [ ] Screenshots are current
- [ ] License selected and included

## Final release

- [ ] Version number selected
- [ ] Changelog updated
- [ ] Final clean-install test completed
- [ ] Git working tree clean
- [ ] Release commit pushed
- [ ] Release tag created
