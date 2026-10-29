---
name: postgres-performance
description: Tune Postgres runtime performance — pg_stat_statements, vacuum/bloat/HOT, index types, locks, pooling. Not server config (audit-pg-config).
---

# postgres-performance

> Postgres performance is MVCC economics: every update writes a new row version, and vacuum, indexes, and long transactions decide whether that stays cheap. Measure with the catalog, then change one thing.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A Postgres workload is slow, bloated, lagging replicas, or burning IO/CPU and you need Postgres-specific causes and fixes.
- Designing a high-write or large-table Postgres schema (queue table, event log, time series) for performance.
- Following `polymath-database:db-performance-triage` once the engine is confirmed as Postgres.

Not this when: you only need the server parameters sanity-checked — `polymath-backend:audit-pg-config`. For reading one plan — `polymath-data:sql-optimize`; for lock review of a schema change — `polymath-backend:review-migration`.

## Inputs

- Postgres version (features differ: `pg_stat_io` and `MERGE` need 15–16+, `INCLUDE` indexes 11+, partition pruning improved through 12–14), managed/self-hosted, RAM/vCPU/storage.
- Output of the catalog queries in [references/catalog-queries.md](references/catalog-queries.md) for the affected window; `pg_stat_statements` must be enabled or say so.
- The workload shape: OLTP / queue / append-only / analytics, write rate, table sizes, and the pooler in front (PgBouncer mode).

**Read-only.** `SELECT`/`SHOW`/`EXPLAIN` only; `EXPLAIN ANALYZE` of writes inside `BEGIN … ROLLBACK` and preferably on a replica. Never run `VACUUM FULL`, `REINDEX`, `ALTER SYSTEM`, or `pg_terminate_backend` from this skill — recommend; the owner applies.

## Procedure

1. **Find the load.** Rank `pg_stat_statements` by `total_exec_time` and by `calls`; for the top few note `mean_exec_time`, `rows`, `shared_blks_read`, `temp_blks_written`. Sample `pg_stat_activity` wait events repeatedly (`IO:DataFileRead`, `LWLock:*`, `Lock:transactionid`, `Client:ClientRead`, `IPC:*`). `Client:ClientRead` dominating means the app, network, or an idle-in-transaction pattern — not the database.
2. **Read plans the Postgres way.** `EXPLAIN (ANALYZE, BUFFERS, SETTINGS)`: actual vs estimated rows (an order-of-magnitude drift means stats or correlation problems), `Rows Removed by Filter`, `Heap Fetches` on an Index Only Scan (stale visibility map), `Sort Method: external merge`, `Batches > 1` on hash (spill), nested loop with high `loops`. Fixes in order: `ANALYZE`; raise per-column `STATISTICS` or add extended statistics (`CREATE STATISTICS … (dependencies, ndistinct, mcv)`) for correlated columns; then index/query changes. Never leave `enable_seqscan = off` in place.
3. **Index kind and shape.** B-tree default; partial indexes for queue/status predicates; `INCLUDE` for covering hot reads; GIN for JSONB/array/FTS (`gin_pending_list` and `fastupdate` trade write latency for throughput); BRIN for huge append-only, time-correlated tables; `pg_trgm` for `LIKE '%x%'`. Build with `CREATE INDEX CONCURRENTLY`; check for leftover `INVALID` indexes. Full design in `polymath-database:index-strategy`.
4. **MVCC, vacuum, bloat.**
   - Dead tuples accumulate on every `UPDATE`/`DELETE`; autovacuum reclaims them if nothing pins the xmin horizon. The usual blockers: long transactions, `idle in transaction`, forgotten replication slots, `hot_standby_feedback` with long replica queries, orphaned prepared transactions. Find the oldest xmin holder before touching vacuum settings.
   - Lower `autovacuum_vacuum_scale_factor` (and set `autovacuum_vacuum_insert_scale_factor` for append-only tables — freezes and the visibility map need it) per large table; raise `autovacuum_vacuum_cost_limit` if autovacuum can't keep pace on fast storage.
   - **HOT updates** avoid index writes when no indexed column changes and the page has room: set `fillfactor` 70–90 on hot-update tables and don't index frequently updated columns. Check `n_tup_hot_upd / n_tup_upd` in `pg_stat_user_tables`.
   - Transaction ID wraparound: monitor `age(datfrozenxid)` / `relfrozenxid`; anti-wraparound vacuums are not cancellable and not optional.
5. **Queue/hot-row patterns.** A table used as a queue churns dead tuples — use `FOR UPDATE SKIP LOCKED` with a partial index on the pending predicate, delete/archive in batches, and vacuum aggressively (or partition and drop). Counters and "latest" rows serialize on one tuple: shard the counter, append-and-aggregate, or move to a cache.
6. **Partitioning.** Declarative range/list partitioning helps when (a) queries filter on the partition key so pruning works, (b) you drop old data by detaching/dropping partitions instead of `DELETE`, (c) vacuum/index builds on a monolith hurt. It does not speed up queries that don't prune, and partition counts in the thousands slow planning. See `polymath-database:partitioning-sharding`.
7. **Connections and pooling.** Each backend is a process; > a few hundred active connections thrash. Put PgBouncer in `transaction` mode (no session state: prepared statements, `SET`, advisory locks, `LISTEN` need care), size the server pool to roughly cores × 2–4 for active work, and keep `max_connections` modest. Fix the app's pool size before raising server limits.
8. **Locks and contention.** `pg_blocking_pids`, `log_lock_waits`, `deadlock_timeout`. Common causes: long transactions holding row locks, `ALTER TABLE` queued behind a long query (and blocking everything behind it — set `lock_timeout`), foreign-key checks on unindexed referencing columns, `SELECT … FOR UPDATE` on hot parents. Index every foreign key's referencing column unless you've shown it unneeded.
9. **WAL, checkpoints, replicas.** `pg_stat_wal`/checkpointer stats for checkpoint pressure (`max_wal_size`, `checkpoint_timeout`, `wal_compression`); replica `replay_lag` and recovery conflicts; inactive replication slots retaining WAL (`max_slot_wal_keep_size`). Offload read-only reporting to replicas only after accounting for lag and feedback bloat.
10. **Memory knobs, last.** `work_mem` is per sort/hash node per connection — raise per session for the job that needs it, not globally; `effective_cache_size` informs the planner but allocates nothing; `shared_buffers` ~25% RAM is the usual start; `maintenance_work_mem` speeds index builds and vacuum. Server-level audit is `polymath-backend:audit-pg-config`.
11. **Change one thing, re-measure** with the same queries and reset deltas (`pg_stat_statements_reset()` only on a system you own; otherwise diff two snapshots).

## Output

```text
Postgres performance review: ledger-db (PG 15, 32 vCPU / 256 GB, PgBouncer transaction mode)

Load (pg_stat_statements, 24 h)
  #1 UPDATE accounts SET balance … WHERE id=$1      38% total · 9k calls/s · mean 1.1 ms · HOT ratio 4%
  #2 SELECT … FROM entries WHERE account_id=$1 AND posted_at > $2   27% total · 6k/s · mean 2.0 ms · heap fetches 61%
Waits: 44% IO:DataFileRead, 18% LWLock:WALWrite, 9% Lock:transactionid

Findings
  1. accounts is updated on an indexed column (updated_at in accounts_updated_idx) → HOT 4%; every update rewrites 4 indexes.
     Fix: drop accounts_updated_idx (0 reads); set fillfactor 80 via a table rewrite in a maintenance window; expect HOT ratio > 80%.
  2. entries index-only scan does heap fetches 61% → visibility map stale; autovacuum_vacuum_insert_scale_factor is default.
     Fix: per-table autovacuum_vacuum_insert_scale_factor = 0.02; verify Heap Fetches → ~0.
  3. Oldest xmin holder: replication slot "bi_etl" inactive 3 d, pinning 220 GB WAL and vacuum.
     Fix: confirm the consumer is gone, drop the slot; set max_slot_wal_keep_size.
Not the cause (checked): connections (active 31), checkpoints (timed 96%), planner estimates (within 2×).
Order: 3 → 2 → 1 (risk ascending; 1 needs a rewrite window).
Verify: accounts HOT ratio, entries Heap Fetches, WAL retained, p99 of #1 and #2.
Unknowns: [VERIFY: bi_etl slot is truly abandoned — ask its owner before dropping].
```

## Quality bar

- Findings cite catalog evidence (a `pg_stat_*` view, a plan field, a wait event), not folklore.
- The xmin horizon is checked before any vacuum or bloat remedy is proposed.
- Fixes name the verification metric; destructive steps (`REINDEX`, rewrite, slot drop) carry a rollback or owner-confirmation note.
- Version-dependent features are stated with the version needed.
- Connection pooling constraints (transaction mode vs session state) are respected in recommendations.

## Anti-patterns to avoid

- Raising `max_connections` or `work_mem` globally as the first move.
- Disabling autovacuum "for now", or running `VACUUM FULL` on a hot table (it takes an `ACCESS EXCLUSIVE` lock and rewrites it).
- Adding an index to a high-write table without checking HOT impact and write cost.
- Using `enable_*` planner switches, or hints, as the permanent fix instead of fixing statistics.
- A long-lived `idle in transaction` session, or an unbounded transaction around a batch job.
- Partitioning a table whose queries never filter on the partition key.
