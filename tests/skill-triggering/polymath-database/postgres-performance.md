---
plugin: polymath-database
skill: postgres-performance
trigger_prompts:
  - "postgres autovacuum can't keep up and we have 40% bloat on a hot table"
  - "HOT updates are only 4% on our Postgres accounts table"
  - "tune Postgres pg_stat_statements top queries and idle in transaction sessions"
must_invoke:
  - polymath-database:postgres-performance
allow_invoke:
  - polymath-backend:audit-pg-config
  - polymath-database:db-performance-triage
  - polymath-data:sql-optimize
  - polymath-core:*
---

# Why this test exists

Confirms the description routes these natural phrasings to `polymath-database:postgres-performance` rather than to its sibling skills.
