---
name: sql-optimize
description: Read EXPLAIN ANALYZE output and propose targeted optimizations — index, predicate, join order, or query shape changes.
---

# sql-optimize

> A SQL query is slow. Read the plan, identify the dominant cost, propose one concrete change.

## When to use

- A query is slow in production or in development.
- A scheduled report has crept up over time and you want to know why.

## Inputs

- The query.
- The plan: `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` on Postgres (or the dialect equivalent). Run with a warmed cache when comparing.
- Schema and indexes for the involved tables.

## Procedure

1. **Read the plan bottom-up**. The expensive nodes are usually the leaves (sequential scans, large hash builds).
2. **Look for**:
   - **Seq Scan on a large table** with a selective predicate → missing or unused index.
   - **Index Scan** on the wrong index (high "buffers read" relative to rows returned) → composite index column order is wrong.
   - **Nested Loop** with high outer rows → join order / hash join would be cheaper.
   - **Sort** spilling to disk (high "external merge" or "Sort Method: external") → memory or pre-sorted index.
   - **Hash Aggregate** with very high `Rows Removed by Filter` → predicate could move earlier.
   - **Function call in WHERE** (`WHERE lower(email) = ...`) blocking index use → use a functional index or normalize on write.
   - **CTE materialization** on Postgres < 12 (CTEs are an optimization fence in old versions) → inline or use a subquery.
3. **Compute the dominant cost**. Pick the single node accounting for > 50% of total runtime; if no single node dominates, pick the deepest one.
4. **Propose ONE change**. State the expected effect with a rationale, then verify with a fresh `EXPLAIN ANALYZE` of the patched query.

## Output

```text
Slow query: top countries by active users.

Plan summary:
  - Total: 4,200 ms.
  - Dominant: Seq Scan on events (3,800 ms, 12M rows, returns 480k).
  - Predicate: created_at >= now() - interval '7 days' AND country_code IS NOT NULL.

Diagnosis:
  events.created_at is indexed but the planner picked Seq Scan because
  the optimizer's row estimate for the predicate is off by 10x.

First fix:
  ANALYZE events;
  Re-run EXPLAIN. If the planner still picks Seq Scan, force-test with
    SET enable_seqscan = off;
  to confirm the index would be cheaper.

Likely permanent fix:
  Composite index events(created_at, country_code).
  Drop the standalone events(country_code) index if unused.
```

## Anti-patterns to avoid

- "Add an index" without checking pg_stat_user_indexes for unused ones first.
- Rewriting the query before reading the plan.
- Comparing runtimes on a cold vs warm cache.
- Changing multiple things at once and not knowing which helped.
