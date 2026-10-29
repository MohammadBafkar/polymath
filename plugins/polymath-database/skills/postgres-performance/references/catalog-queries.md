# Postgres catalog queries (read-only)

Run against a replica or off-peak primary. Column names are for PG 13+ (`total_exec_time`); on PG ≤ 12 use `total_time` / `mean_time`.

## Top statements

```sql
SELECT queryid, calls,
       round(total_exec_time::numeric, 1)  AS total_ms,
       round(mean_exec_time::numeric, 2)   AS mean_ms,
       rows, shared_blks_hit, shared_blks_read, temp_blks_written,
       left(query, 100) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 15;
```

## Wait-event sample (run ~10× a few seconds apart)

```sql
SELECT wait_event_type, wait_event, state, count(*)
FROM pg_stat_activity
WHERE backend_type = 'client backend' AND state <> 'idle'
GROUP BY 1,2,3 ORDER BY 4 DESC;
```

## Oldest xmin holders (what blocks vacuum)

```sql
-- long / idle-in-transaction sessions
SELECT pid, state, now() - xact_start AS xact_age, backend_xmin, left(query, 80)
FROM pg_stat_activity
WHERE backend_xmin IS NOT NULL ORDER BY age(backend_xmin) DESC LIMIT 10;
-- replication slots
SELECT slot_name, active, restart_lsn, xmin, catalog_xmin,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal
FROM pg_replication_slots;
-- prepared transactions
SELECT gid, prepared, owner FROM pg_prepared_xacts;
```

## Dead tuples, vacuum lag, HOT ratio

```sql
SELECT relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       round(100.0 * n_tup_hot_upd / nullif(n_tup_upd, 0), 1)             AS hot_pct,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 15;
```

## Sequential scans on big tables

```sql
SELECT relname, seq_scan, seq_tup_read, idx_scan,
       pg_size_pretty(pg_relation_size(relid)) AS size
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC LIMIT 15;
```

## Unused and duplicate indexes (check the stats window first)

```sql
SELECT s.relname AS table, s.indexrelname AS index, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS size,
       i.indisunique, i.indisprimary
FROM pg_stat_user_indexes s JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0 AND NOT i.indisunique AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC LIMIT 20;
SELECT stats_reset FROM pg_stat_database WHERE datname = current_database();
```

Also confirm the index doesn't back a foreign-key lookup that is rare but critical, and check replicas — usage is per node.

## Foreign keys without a supporting index on the referencing side

```sql
SELECT c.conrelid::regclass AS table, c.conname, a.attname AS column
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND i.indkey[0] = c.conkey[1]);
```

(First column only; multi-column keys need a prefix check.)

## Cache and temp spill

```sql
SELECT datname, blks_hit, blks_read,
       round(100.0 * blks_hit / nullif(blks_hit + blks_read, 0), 2) AS hit_pct,
       temp_files, pg_size_pretty(temp_bytes) AS temp
FROM pg_stat_database WHERE datname = current_database();
```

## Wraparound headroom

```sql
SELECT datname, age(datfrozenxid) AS xid_age,
       round(100.0 * age(datfrozenxid) / 2147483648, 1) AS pct_to_wraparound
FROM pg_database ORDER BY 2 DESC;
```

## Replication lag

```sql
SELECT application_name, state, sync_state, replay_lag, write_lag, flush_lag
FROM pg_stat_replication;
```

## Plan with everything

```sql
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, SETTINGS, VERBOSE) <statement>;
ROLLBACK;
```
