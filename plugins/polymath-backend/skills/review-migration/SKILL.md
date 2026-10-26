---
name: review-migration
description: Review a Postgres migration for lock surface, online/offline safety, backfill strategy — flags ACCESS EXCLUSIVE locks and unsafe defaults on large tables.
---

# review-migration

> Review a `.sql` migration the way an on-call reviewer would: which lock does each statement need, how long it holds, and whether it's safe to apply against a live, replicating, big-table prod.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A schema migration is in a PR.
- A long-lived table needs a structural change and someone has drafted SQL.
- A previous migration timed out and you're trying to figure out why.

## Inputs

- The migration `.sql` file(s) (required). For ORM migrations, review the generated SQL (`rails db:migrate:status` + `--dry-run`, `alembic upgrade --sql`, `prisma migrate diff --script`), not the DSL.
- The Postgres major version (required — PG 11 fast defaults and PG 12 `NOT NULL`-via-`CHECK` change the verdict). Unknown: ask; unattended, assume the oldest version the repo supports and say so.
- Table sizes and write rates (optional) — unknown tables are treated as large and hot.

## Related skills

- [`polymath-backend:migration-plan`](../../../polymath-backend/skills/migration-plan/SKILL.md)
  — vendor-agnostic expand-migrate-contract phasing for online
  migrations. Plan the phases there; review each Postgres-specific
  statement here.
- [`polymath-backend:audit-pg-config`](../audit-pg-config/SKILL.md)
  — review the Postgres server configuration the migration will run
  against.

## Procedure

0. **Deterministic baseline.** If `squawk` (the Postgres migration linter) is available — `squawk <file>.sql`, or `npx squawk-cli` — run it first and fold its rule hits into the statement list; never report a statement as safe that it flags without saying why it doesn't apply.
1. **Parse statements.** For each statement, identify the locks acquired and held:
   - `CREATE INDEX` — `SHARE` lock (writes blocked).
   - `CREATE INDEX CONCURRENTLY` — `SHARE UPDATE EXCLUSIVE` lock (writes ok); cannot run inside a transaction.
   - `ALTER TABLE … ADD COLUMN` (without default) — `ACCESS EXCLUSIVE`, fast (PG 11+ tracks default separately).
   - `ALTER TABLE … ADD COLUMN … DEFAULT <volatile>` — `ACCESS EXCLUSIVE`, rewrites the table (slow + outage on large tables).
   - `ALTER TABLE … ADD COLUMN … DEFAULT <constant>` (PG 11+) — fast; uses fast-default optimization.
   - `ALTER TABLE … SET NOT NULL` — `ACCESS EXCLUSIVE`, full scan unless a validated `CHECK (col IS NOT NULL)` constraint already exists (PG 12+ uses it to skip the scan; older versions always scan).
   - `ALTER TABLE … ALTER COLUMN … TYPE` — `ACCESS EXCLUSIVE` and usually a full table rewrite (binary-coercible changes such as widening a `varchar` are the exception).
   - `ALTER TABLE … ADD CONSTRAINT … UNIQUE / PRIMARY KEY` — builds the index under `ACCESS EXCLUSIVE`; instead `CREATE UNIQUE INDEX CONCURRENTLY`, then `ADD CONSTRAINT … USING INDEX`.
   - `ALTER TABLE … DROP COLUMN` — `ACCESS EXCLUSIVE`, metadata-only (fast).
   - `RENAME` — `ACCESS EXCLUSIVE`, but instant. Watch out for app code still using the old name.

   **Even "instant" `ACCESS EXCLUSIVE` statements are dangerous on a busy table**: the lock request waits behind any long-running transaction, and every new query queues behind *it* — a metadata-only change can stall all traffic. That is why step 6's `lock_timeout` is non-negotiable.
2. **Backfill plan.** If the migration rewrites data:
   - Batch in chunks with explicit commits. Postgres `UPDATE` has no `LIMIT` — batch by primary-key range or a sub-select:
     `UPDATE refunds SET currency = 'USD' WHERE id IN (SELECT id FROM refunds WHERE currency IS NULL ORDER BY id LIMIT 10000);`
   - Run outside the schema-migration tool (which usually wraps in a single tx).
   - Pace by `pg_sleep` or external orchestration so the WAL backlog stays manageable.
3. **`NOT NULL` rollout (multi-step).** The safe pattern (PG 12+ for the fast step 4). A `NOT VALID` check is still enforced on every new INSERT/UPDATE — so before step 2, the app must already write the column (or the column needs a `DEFAULT`), or new writes start failing:
   ```sql
   ALTER TABLE refunds ADD COLUMN currency text;            -- step 1
   -- deploy app that always writes currency (or: ALTER COLUMN currency SET DEFAULT 'USD')
   ALTER TABLE refunds ADD CONSTRAINT refunds_currency_not_null
     CHECK (currency IS NOT NULL) NOT VALID;               -- step 2
   -- backfill in batches (see step 2), in its own deploy/job
   ALTER TABLE refunds VALIDATE CONSTRAINT refunds_currency_not_null;  -- step 3
   ALTER TABLE refunds ALTER COLUMN currency SET NOT NULL; -- step 4 (fast because constraint is valid)
   ALTER TABLE refunds DROP CONSTRAINT refunds_currency_not_null;
   ```
4. **Index migrations.** Always `CONCURRENTLY` for production. Note: `CONCURRENTLY` can fail and leave an `INVALID` index — the review should check there's a cleanup statement (`DROP INDEX IF EXISTS … ; CREATE INDEX CONCURRENTLY …`).
5. **Foreign keys.** `ADD CONSTRAINT … FOREIGN KEY … NOT VALID` then `VALIDATE CONSTRAINT` later — same pattern as NOT NULL.
6. **Lock timeout.** Recommend `SET lock_timeout = '5s'` at the top of risky migrations so they fail fast under contention instead of holding the queue.
7. **Statement timeout.** Likewise `SET statement_timeout = '30s'` for individual statements; backfills set their own batch-scoped timeouts.

## Output

```text
review-migration

File:    db/migrations/20260523_add_currency.sql
Target:  refunds (≈ 50M rows)

Statements
  1. ALTER TABLE refunds ADD COLUMN currency text;
     Lock: ACCESS EXCLUSIVE (fast, metadata-only).                ✓

  2. ALTER TABLE refunds ALTER COLUMN currency SET DEFAULT 'USD';
     Lock: ACCESS EXCLUSIVE (fast on PG 11+).                     ✓

  3. ALTER TABLE refunds ALTER COLUMN currency SET NOT NULL;
     Lock: ACCESS EXCLUSIVE; full scan on 50M rows.               ✗ unsafe

Issues
  - Statement 3 holds ACCESS EXCLUSIVE — blocking reads and writes — for the full scan of a 50M-row table.
    Fix: split into the 4-step NOT VALID → backfill → VALIDATE → SET NOT NULL pattern.

  - No lock_timeout set. Risk: migration holds the queue if contention spikes.
    Fix: prepend `SET lock_timeout = '5s';`.

Recommendation: split into 3 deploys (constraint+backfill+set-not-null). Block PR until restructured.
```

## Quality bar

- Every statement classified by lock + cost.
- Multi-step pattern named when a single statement is unsafe.
- `CONCURRENTLY` flagged where it should be present (and not inside a transaction).
- `lock_timeout` / `statement_timeout` recommendations stated.

## Anti-patterns to avoid

- "Just add NOT NULL, the table isn't that big" without measuring. Big tables are big at 3 AM, not at code-review time.
- `CREATE INDEX` (not CONCURRENTLY) on a live table. Writes blocked for the duration.
- Wrapping CONCURRENTLY in a transaction. Postgres rejects; the migration tool may obscure the error.
- Running backfill in a single statement on a 50M-row table. WAL bloat, replica lag, undo time after rollback.
