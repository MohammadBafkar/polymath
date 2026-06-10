# Changelog — polymath-backend

## [Unreleased]

### Added

- `api-design-rest` and `db-schema` consume project localization: `conventions_docs` roles `api-style`/`backend-stack`/`database` from the project-context snapshot.

### Changed

- Added Postgres migration-safety skills `review-migration` and
  `audit-pg-config` (and their `/review-migration` and `/audit-config`
  commands) — migration safety belongs next to `db-schema` and
  `migration-plan`.

## [0.1.0]

### Added

- Initial v0.1 components: `api-design-rest`, `db-schema`, `migration-plan` skills.
