# Changelog — polymath-backend

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 6 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `review-migration`: runs `squawk` first when available as the deterministic baseline; requires the Postgres major version; fixed the example — `ACCESS EXCLUSIVE` blocks reads *and* writes.
- `db-schema`, `migration-plan`, `review-migration`: Inputs sections with missing-data behavior.
- `api-versioning`: exact output shape.

## [0.11.0]

### Fixed

- `review-migration`: Postgres `UPDATE` has no `LIMIT` (batch by key range/sub-select); a `NOT VALID` check still blocks new writes, so the app must write the column first; fast `SET NOT NULL` needs PG 12+; added the lock-queue hazard, `ALTER COLUMN TYPE`, and `UNIQUE … USING INDEX`.
- `migration-plan`: contract is the one-way door (rollback = restore from an archive, not re-adding a column); explicit backfill-complete gate before contract.
- `db-schema`: `gen_random_uuid()` is v4 (v7 via `uuidv7()` on PG 18+ or the app); composite index order is equality-then-range, not "predicate order"; native enums are hard to evolve.
- `api-design-rest`: object-level authorization step; `Idempotency-Key` for `POST`/non-idempotent `PATCH` with key-reuse semantics; RFC 9457 option.
- `api-versioning`: adding an enum value can break strict clients.
- `audit-pg-config`: When-to-use, inputs from `pg_settings`, read-only rule, replication-slot WAL retention.

### Removed

- The `/review-migration` command (the skill is already `/polymath-backend:review-migration`).

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
