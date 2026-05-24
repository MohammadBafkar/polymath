---
plugin: polymath-data
scenario: sql-optimize-slow-aggregation
expect:
  invoked:
    - polymath-data:sql-optimize
  output_matches:
    - "Seq Scan"
    - "index"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> This query is slow. Help me optimize it.

```sql
SELECT country_code, COUNT(*) AS active
FROM events
WHERE created_at >= now() - INTERVAL '7 days'
GROUP BY country_code;
```

EXPLAIN ANALYZE summary (Postgres 15):

```
Seq Scan on events  (cost=0..3800000 rows=480000 width=8)
                    (actual time=12..3800 rows=480000 loops=1)
  Filter: (created_at >= now() - '7 days'::interval)
  Rows Removed by Filter: 11500000
Total runtime: 4200 ms
```

Use polymath-data:sql-optimize.

# Acceptance

- The diagnosis names the Seq Scan as the dominant cost (>50% of runtime).
- The first proposed fix is a composite or appropriate index on
  `events(created_at, country_code)` or equivalent.
- Mentions running `ANALYZE` or considers the planner's row-estimate error.
- Recommends ONE first change, not many.
