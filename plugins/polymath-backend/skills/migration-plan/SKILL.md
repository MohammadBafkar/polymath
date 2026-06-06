---
name: migration-plan
description: Plan a safe online database migration in expand-migrate-contract phases; outputs the ordered steps and the rollback for each.
---

# migration-plan

> Lay out an online schema/data migration without downtime. Every step has a rollback.

## When to use

- A schema change involves rewriting existing rows, changing types, or renaming columns.
- A migration could lock a hot table for too long.
- The user says "is this migration safe?".

## Related skills

- [`polymath-backend:review-migration`](../review-migration/SKILL.md)
  — Postgres-specific statement-level review: per-statement lock
  taxonomy (`ACCESS EXCLUSIVE` vs `SHARE UPDATE EXCLUSIVE`), the safe
  `NOT NULL` multi-step pattern, big-table hazards. Use *this* skill
  to plan the expand-migrate-contract phases; use `review-migration`
  to audit each SQL statement before it ships on Postgres.
- [`polymath-data:sql-write`](../../../polymath-data/skills/sql-write/SKILL.md)
  — for backfill query authoring inside the migrate phase.

## Procedure

Plan in three phases. The app keeps running on the **old** shape during expand,
on **both** shapes during migrate, and on the **new** shape during contract.

1. **Expand** (additive only):
   - Add the new column / table / index with no app code reading it.
   - Defaults must be `NULL` or a non-blocking server-side default — never a backfill in the migration itself.
   - Indexes built with `CREATE INDEX CONCURRENTLY` (Postgres) or the equivalent.
   - Rollback: drop the new object.

2. **Migrate** (dual-write + backfill):
   - App writes to both old and new shape on every mutation.
   - Backfill historic rows in **batches** (a few thousand rows per transaction). Run during low-traffic windows. Use `LIMIT` + a primary-key cursor; never a single huge `UPDATE`.
   - App reads the new shape if it's populated, falling back to the old.
   - Rollback: stop dual-write; drop the new column or table.

3. **Contract** (remove old):
   - App writes only the new shape.
   - Remove old code paths.
   - Drop old columns / tables / indexes.
   - Rollback: re-add the old column (it had to be NULLable to be droppable safely; ensure expand left it that way).

## Specific hazards to plan around

- **Locks**: any `ALTER TABLE` that rewrites the table is a hazard on Postgres / MySQL. Long locks cascade into request timeouts. Confirm the operation is metadata-only or fast.
- **Long index builds**: build concurrently; monitor; ready a kill plan.
- **Type changes**: never change a column type in place on a hot table. Add a new column, dual-write, swap.
- **Renames**: a rename is a type change in disguise. Use add-new + dual-write + drop-old.
- **Nullable → NOT NULL**: only after the backfill is verified to have populated every row. Add the constraint with `NOT VALID` first, then `VALIDATE CONSTRAINT` to avoid a full table scan under a lock.
- **Foreign keys**: add with `NOT VALID` then `VALIDATE` so the validation scan runs without a lock.

## Output

```text
Migration plan: refund_idempotency_keys

Goal: add `idempotency_key varchar(64) UNIQUE` to `refunds`.

Phase 1 — Expand
  1. ALTER TABLE refunds ADD COLUMN idempotency_key varchar(64) NULL;
  2. CREATE UNIQUE INDEX CONCURRENTLY refunds_idem_key_uq
     ON refunds (idempotency_key) WHERE idempotency_key IS NOT NULL;
  Rollback: DROP INDEX … ; ALTER TABLE refunds DROP COLUMN idempotency_key;

Phase 2 — Migrate
  3. Deploy app version that writes idempotency_key on every refund create.
  4. (No backfill needed — historic refunds have no idempotency key by
     design; the partial unique index covers this.)
  Rollback: revert app deploy.

Phase 3 — Contract
  5. No-op — column stays NULL for historic rows; new rows always populated.

Monitoring during phases:
  - Lock wait time on refunds.
  - Refund p99 latency.
  - Idempotency-Key collision rate (should be > 0 once retries are observed).
```

## Anti-patterns to avoid

- Mixing expand + migrate + contract in one deploy.
- Backfilling in a single `UPDATE` on a large hot table.
- Adding `NOT NULL` to an existing column in one step on a populated table.
- Dropping a column the same release it stops being read.
