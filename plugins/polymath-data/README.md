# polymath-data

Data craft for the Polymath marketplace.

## What it ships

- Skills:
  - [`sql-write`](skills/sql-write/SKILL.md) — translate a question
    into a parameterized, dialect-aware SQL query with the assumed
    schema documented inline.
  - [`sql-optimize`](skills/sql-optimize/SKILL.md) — read
    `EXPLAIN ANALYZE` / query-profile output across Postgres, MySQL,
    SQLite, BigQuery, Snowflake, Redshift, DuckDB; propose one
    targeted optimization.
  - [`metrics-tree`](skills/metrics-tree/SKILL.md) — decompose a
    headline metric into the smallest set of drivers that explains
    movement.
  - [`run-experiment`](skills/run-experiment/SKILL.md) — plan an A/B
    or A/B/n experiment with hypothesis, primary + guardrail
    metrics, MDE + sample size + duration, randomization, stop
    conditions.

## Scope and deferrals

`polymath-data` is intentionally **narrow**: SQL authoring + plan
reading, metric trees, and experiment design. It does **not** ship
skills for the full data-engineering / data-science stack today.

When the work needs an adjacent surface, defer:

- **Schema migrations** —
  [`polymath-backend:migration-plan`](../polymath-backend/skills/migration-plan/SKILL.md)
  for expand-migrate-contract phasing;
  [`polymath-infra-postgres:review-migration`](../polymath-infra-postgres/skills/review-migration/SKILL.md)
  for Postgres-specific lock review.
- **Database server configuration** —
  [`polymath-infra-postgres:audit-pg-config`](../polymath-infra-postgres/skills/audit-pg-config/SKILL.md).
- **Data pipelines / ETL / orchestration** — currently deferred to
  external catalogs (dbt project conventions, Airflow / Dagster
  community docs). When a Polymath workflow shape becomes load-bearing,
  a focused skill will be added here.
- **Data science / model evaluation** — deferred to
  [`polymath-ai:eval-plan`](../polymath-ai/skills/eval-plan/SKILL.md)
  for evaluation harness design, and to external ML / AI skill
  catalogs for model authoring.

See [`LIMITATIONS.md`](../../LIMITATIONS.md) § 3 for the catalog-wide
"intentionally thin" stance.

## Installation

```bash
claude plugin install polymath-data@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
