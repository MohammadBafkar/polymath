# Changelog — polymath-backend

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Backend craft: REST API design, API versioning strategy, relational schema design, safe online migrations.

### Skills

- **api-design-rest** — Design a REST endpoint or resource — URL, method, status codes, request/response shape, errors, idempotency, versioning.
- **api-versioning** — Plan an API versioning strategy — URL vs header vs media-type versioning, semantic rules, backward-compatible change classification, consumer-driven contracts, deprecation path.
- **audit-pg-config** — Audit Postgres server config — shared_buffers, work_mem, max_connections vs pgbouncer pool, autovacuum tuning, WAL retention.
- **db-schema** — Design or review a relational schema — tables, columns, types, indexes, constraints, naming, soft-delete and audit decisions.
- **migration-plan** — Plan a safe online database migration in expand-migrate-contract phases; outputs the ordered steps and the rollback for each.
- **review-migration** — Review a Postgres migration for lock surface, online/offline safety, backfill strategy — flags ACCESS EXCLUSIVE locks and unsafe defaults on large tables.

### Commands

- **/audit-config** — Audit Postgres server config — memory, connections, WAL, autovacuum, logging.
- **/review-migration** — Review a pending DB migration before merging; command entry point for the review-migration skill.
