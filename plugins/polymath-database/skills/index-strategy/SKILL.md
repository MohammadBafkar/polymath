---
name: index-strategy
description: Design or prune indexes from the query workload — column order, covering, partial, type, write cost, unused cleanup. Not plan reading.
---

# index-strategy

> An index is a trade: faster reads for slower writes, more storage, and more maintenance. Design the smallest set that serves the workload's actual predicates and sorts.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A table is slow to read, or a new feature adds queries and you need to know which indexes it needs.
- Write latency or storage is climbing and you suspect too many indexes.
- Reviewing a migration that adds, drops, or changes an index.

Not this when: you have a single slow query and want the plan read — `polymath-data:sql-optimize`. The migration mechanics of shipping the index — `polymath-backend:migration-plan`.

## Inputs

- The query workload for the table: the top statements by total time with their predicates, joins, `ORDER BY`, and calls/sec (from `polymath-database:db-performance-triage` or the statements view). Without a workload, say so — an index designed without queries is a guess.
- Table size and growth, write rate, existing indexes with usage counts, and column cardinality/skew (`pg_stats`, `INFORMATION_SCHEMA.STATISTICS`, or the engine equivalent).
- Engine and version — index types, `INCLUDE`, partial/expression support, and online-build options differ.

**Read-only.** Never create or drop an index on a live system from this skill. Recommend the DDL; creation goes through a reviewed migration (online build: `CREATE INDEX CONCURRENTLY` on Postgres, `ALGORITHM=INPLACE, LOCK=NONE` on MySQL, `ONLINE = ON` on SQL Server Enterprise).

## Procedure

1. **List the access patterns**, not the columns: each as `table · filter predicates (= / range / IN / LIKE) · join keys · sort · limit · calls/sec`. Group patterns that share a prefix — one index often serves several.
2. **Choose the column order for each composite index** (B-tree):
   - Equality columns first, then the range or sort column, then the rest — the leftmost-prefix rule. An index on `(a, b)` serves `a = ?` and `a = ? AND b …`; it does not serve `b = ?` alone.
   - Among equality columns, order by how often the column is filtered, then selectivity, but never let a high-cardinality tiebreak push a range column ahead of equality columns.
   - Make `ORDER BY` free: if the sort follows the equality prefix (`WHERE customer_id = ? ORDER BY created_at DESC LIMIT 20`), `(customer_id, created_at DESC)` returns rows pre-sorted and stops after 20 — no sort node.
3. **Pick the index kind** for the predicate: B-tree (equality, range, sort — the default); hash (equality only, rarely worth it); GIN (arrays, JSONB containment, full-text); GiST/SP-GiST (geometry, ranges, nearest-neighbour); BRIN (huge append-only tables physically correlated with the column, e.g. a timestamp — tiny and cheap, useless if rows are shuffled); bitmap/columnstore on analytical engines; text/vector indexes (IVFFlat/HNSW) for similarity search. State why the default isn't enough.
4. **Cut the index size and write cost:**
   - **Covering**: add `INCLUDE (cols)` (Postgres 11+, SQL Server) or trailing columns so the query is index-only — but only for hot, narrow reads; wide covering indexes cost more than they save. Index-only scans in Postgres also need a recently vacuumed visibility map.
   - **Partial**: `WHERE status = 'pending'` indexes only the rows the queue query touches; a fraction of the size and write cost. The query's predicate must imply the index predicate.
   - **Expression**: `(lower(email))` when queries use the function; the query must use the identical expression.
   - **Unique** where the domain demands it — it is both an index and an invariant.
5. **Estimate the write cost.** Each index adds work to every `INSERT`, to `UPDATE`s that touch indexed columns (and in Postgres defeats HOT updates), and to `DELETE`; also storage and replication/WAL volume. Tables with >5–6 indexes and high write rates need a justification per index.
6. **Prune.** Candidates to drop: zero scans over a full business cycle (`pg_stat_user_indexes.idx_scan`, MySQL `sys.schema_unused_indexes`, SQL Server `sys.dm_db_index_usage_stats`) *after* checking stats weren't recently reset and it doesn't enforce a constraint or serve a rare-but-critical job (month-end, failover); exact duplicates; strict prefixes of another index (`(a)` when `(a, b)` exists — unless the shorter one is `UNIQUE` or much smaller matters). Drop one at a time, keep the DDL to recreate it, watch for plan regressions.
7. **Verify, don't assume.** For each proposed index, state the expected plan change (Seq Scan → Index Scan/Index Only Scan, sort node disappears) and check it on production-sized data with `EXPLAIN (ANALYZE, BUFFERS)` — the planner may still prefer a scan if the predicate matches a large fraction of the table, if statistics are stale (`ANALYZE`), or if a cast/function defeats the index.
8. **Plan the rollout** through `polymath-backend:migration-plan` / `review-migration` (concurrent build, invalid-index cleanup, disk headroom for the build, replica lag).

## Output

```text
Index plan: orders (214M rows, 1.8k writes/s, 9 indexes)

Access patterns
  P1  WHERE customer_id=? ORDER BY created_at DESC LIMIT 20          18k/s  41% of DB time
  P2  WHERE status='pending' AND created_at < now()-interval '15m'     40/s   queue sweeper
  P3  WHERE lower(email)=?                                             300/s  login lookup

Add
  orders_cust_created   btree (customer_id, created_at DESC)           serves P1; removes the sort; replaces orders_customer_idx
  orders_pending_part   btree (created_at) WHERE status='pending'      serves P2; ~0.3% of rows → a small fraction of a full index's size
  users_email_lower     btree (lower(email)) — UNIQUE                  serves P3; also enforces case-insensitive uniqueness

Drop (after review window)
  orders_customer_idx          strict prefix of orders_cust_created
  orders_status_idx            0 scans in 90 d (stats last reset 2025-05-02); not a constraint
  orders_created_idx_old       identical definition to orders_created_idx (btree created_at)

Write-cost delta: net −1 index on orders → inserts ≈ 8% cheaper [VERIFY: measure insert p95 before/after].
Expected plan change: P1 Seq Scan → Index Scan, no Sort node; verify with EXPLAIN (ANALYZE, BUFFERS) on the replica.
Rollout: CREATE INDEX CONCURRENTLY; 38 GB free disk needed; check pg_index.indisvalid after; drop old indexes in a later migration.
Unknowns: [TBD: month-end reporting query set — confirm orders_status_idx isn't used by it before dropping].
```

## Quality bar

- Every index traces to a named access pattern with its frequency; an index without a pattern isn't proposed.
- Composite column order is justified (equality → range/sort), and the sort-elimination claim is stated where it applies.
- The write-side cost and the drop list are present — a plan that only adds indexes is incomplete.
- Unused-index claims state the stats window and rule out constraints and rare critical jobs.
- Expected plan change and the verification step are explicit.

## Anti-patterns to avoid

- One index per column ("index everything"): the planner rarely combines them well, and writes pay for all of them.
- Putting the range column before equality columns, or the low-selectivity column first by habit.
- Wrapping an indexed column in a function or implicit cast in the query (`WHERE created_at::date = …`, `WHERE varchar_col = 123`) and then blaming the index.
- Leading-wildcard `LIKE '%x'` expecting a B-tree to help — use trigram (`pg_trgm` GIN) or full-text search.
- Dropping an "unused" index right after a stats reset, a failover (stats on the replica differ), or before the monthly job runs.
- Building a large index with a blocking lock on a live table.
