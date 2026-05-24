---
name: db-schema
description: Design or review a relational schema — tables, columns, types, indexes, constraints, naming, soft-delete and audit decisions.
---

# db-schema

> Sketch a relational schema before the first migration. Output is DDL + the rationale.

## When to use

- A new feature needs a new table or column.
- An existing schema is being refactored and you want a second look.
- Migration planning needs a target shape.

## Procedure

1. **Naming** — match the repo's convention (`snake_case` is the safe default for SQL). Tables plural, columns singular, foreign keys `<other_table_singular>_id`.
2. **Identifiers** — pick once per service:
   - `bigint` auto-increment (simple, sortable, leaks count).
   - `uuid` v4 (no count leak, no order).
   - `uuid` v7 / ULID (sortable, no count leak — usually best).
3. **Primary types**:
   - Strings: `varchar(N)` with a sized cap, or `text` with a check constraint. Avoid unbounded `text` for indexed columns.
   - Money: integer in the smallest unit (`amount_cents`). Never floats.
   - Time: `timestamptz` always. Store UTC. Never `timestamp without timezone`.
   - Booleans: `boolean not null default false` — never nullable booleans.
   - Enums: native enum if the DB supports it; otherwise a check constraint + a lookup table.
4. **Required vs nullable** — `not null` until proven otherwise. Nullable means "we know we don't know". Each nullable column needs a justification comment.
5. **Indexes**:
   - Every foreign key gets an index.
   - Every `WHERE` predicate from the top-3 queries gets an index.
   - Composite index column order matches predicate order: most-selective first, range last.
   - Unique constraints exposed as indexes.
6. **Audit columns** — `created_at timestamptz not null default now()`, `updated_at timestamptz not null default now()` with a trigger.
7. **Soft delete** — only if you genuinely need recovery. Add `deleted_at timestamptz` and *every* query needs to filter on it; if you can't enforce that, prefer hard delete + a separate archive table.
8. **Constraints** — encode invariants in the schema: check constraints for value ranges, partial unique indexes for "unique among non-deleted", foreign keys with explicit `on delete` behavior.

## Output

```sql
-- Resource: refunds
CREATE TABLE refunds (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id        uuid NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
  amount_cents    bigint NOT NULL CHECK (amount_cents > 0),
  reason          varchar(120) NOT NULL,
  refund_to       varchar(20) NOT NULL CHECK (refund_to IN ('original','credit')),
  status          varchar(20) NOT NULL CHECK (status IN ('processing','succeeded','failed')),
  idempotency_key varchar(64) UNIQUE,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX refunds_order_id_idx ON refunds (order_id);
CREATE INDEX refunds_status_created_at_idx ON refunds (status, created_at);
```

Rationale:

- `id` uuid v7 via `gen_random_uuid()` substitute on the app side.
- `amount_cents` integer to avoid float drift.
- Index `(status, created_at)` for the "list pending refunds in order" query.
- `idempotency_key` unique so retries collapse to one row.

## Anti-patterns to avoid

- `float` for money.
- `varchar(255)` everywhere "just in case".
- Nullable booleans.
- Unbounded text for columns that are indexed or queried with `LIKE`.
- Missing indexes on foreign keys (the most common slow-query cause).
