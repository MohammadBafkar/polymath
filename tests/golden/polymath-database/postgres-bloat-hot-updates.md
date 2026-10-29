---
plugin: polymath-database
scenario: postgres-bloat-hot-updates
expect:
  invoked:
    - polymath-database:postgres-performance
  output_matches:
    - "(HOT|fillfactor)"
    - "(xmin|replication slot|idle in transaction)"
    - "(autovacuum)"
timeout_seconds: 120
---

# Prompt

> Our Postgres accounts table is updated 9k times/s, autovacuum can't keep up, and replicas lag. pg_stat_user_tables shows 4% HOT updates. What should we look at and change?

Use polymath-database:postgres-performance.

# Acceptance

- Checks what pins the xmin horizon before touching vacuum settings.
- Explains HOT updates, indexed-column updates and fillfactor.
- Per-table autovacuum settings; no VACUUM FULL on the hot table.
- Each fix has a verification metric.
