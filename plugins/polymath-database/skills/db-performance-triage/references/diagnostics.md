# Diagnostic sources by engine

Read-only sources for each triage layer. Run against a replica when the primary is already struggling.

## Postgres

| Layer | Source |
| --- | --- |
| Top statements | `pg_stat_statements` (needs `shared_preload_libraries`): `SELECT queryid, calls, total_exec_time, mean_exec_time, rows, shared_blks_hit, shared_blks_read, temp_blks_written FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;` (column is `total_time` before PG 13) |
| Waits / sessions | `SELECT state, wait_event_type, wait_event, count(*) FROM pg_stat_activity WHERE state <> 'idle' GROUP BY 1,2,3 ORDER BY 4 DESC;` — sample repeatedly; one snapshot lies |
| Idle in transaction | `SELECT pid, now()-xact_start AS age, query FROM pg_stat_activity WHERE state='idle in transaction' ORDER BY age DESC;` |
| Blocking | `SELECT pid, pg_blocking_pids(pid) AS blockers, wait_event_type, query FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;` |
| Cache / IO | `pg_stat_database` (`blks_read`, `blks_hit`, `temp_files`), `pg_statio_user_tables`, `pg_stat_io` (PG 16+); `track_io_timing = on` for read/write time |
| Index use | `pg_stat_user_indexes` (`idx_scan = 0` since last stats reset ⇒ unused candidate); `pg_stat_user_tables` (`seq_scan`, `seq_tup_read`, `n_dead_tup`, `last_autovacuum`) |
| Checkpoints / WAL | `pg_stat_bgwriter` / `pg_stat_checkpointer` (PG 17+): requested vs timed checkpoints; `pg_stat_wal` |
| Replication | `pg_stat_replication` (`replay_lag`), `pg_replication_slots` (inactive slots retain WAL) |

## MySQL / MariaDB

- Statements: `performance_schema.events_statements_summary_by_digest` ordered by `SUM_TIMER_WAIT`; slow query log with `long_query_time`.
- Waits: `performance_schema.events_waits_summary_global_by_event_name`; `sys.schema_unused_indexes`; `sys.statement_analysis`.
- InnoDB: `SHOW ENGINE INNODB STATUS` (latest deadlock, history list length, buffer pool hit); `innodb_buffer_pool_wait_free` > 0 means the pool is too small.
- Locks: `performance_schema.data_lock_waits` (8.0+), `sys.innodb_lock_waits`.

## SQL Server

- Query Store (`sys.query_store_runtime_stats`) for regressions and plan flips; `sys.dm_exec_query_stats` for cumulative cost.
- Waits: `sys.dm_os_wait_stats` (delta between two samples, not the cumulative number); `sys.dm_exec_requests` for live waits.
- Missing indexes: `sys.dm_db_missing_index_details` — hints, not instructions; dedupe before creating.

## Oracle

- AWR / ASH reports (licensed) for top SQL and wait classes; `V$SQL`, `V$SESSION`.

## MongoDB

- `db.currentOp()`, the profiler (`db.setProfilingLevel(1, { slowms: 100 })`), `explain("executionStats")`: compare `totalDocsExamined` / `totalKeysExamined` to `nReturned`; a `COLLSCAN` on a selective filter is the usual lead.

## Host / volume

- Linux: `iostat -x 1` (`%util`, `await`, `aqu-sz`), `vmstat 1` (run queue `r`, swap `si/so`), `pidstat -d`.
- Cloud: volume IOPS and throughput vs provisioned, burst-balance / credit metrics, instance network and EBS-optimized bandwidth limits — a database can be capped by the *instance's* storage bandwidth, not the volume.
