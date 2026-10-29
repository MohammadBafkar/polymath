---
name: db-io-tuning
description: Cut database IO — cache and working set, read/write amplification, WAL/fsync, checkpoints, bloat, volume IOPS limits. Not plans or indexes.
---

# db-io-tuning

> The database is usually IO-bound before it is CPU-bound. Cut the bytes you read and write first; buy faster disks second.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Triage points at IO: waits are `DataFileRead` / `WALWrite` / `log file sync`, volume IOPS or throughput is near its ceiling, or latency tracks storage metrics.
- Write-heavy workload (ingest, queue tables, audit logs) with commit latency spikes or replica lag.
- Sizing storage and instance class for a data set that has outgrown memory.

Not this when: the cause hasn't been located yet — start with `polymath-database:db-performance-triage`. Plan reading is `polymath-data:sql-optimize`; index choice is `polymath-database:index-strategy`.

## Inputs

- IO evidence: read vs write IOPS, throughput, queue depth, and latency over the incident window; cache hit ratio and `blks_read`/`temp` volume from the statements view.
- The working set vs RAM: hot data size (tables + indexes actually touched), total size, buffer/cache size.
- Storage: type and provisioned IOPS/throughput (and the instance's own storage-bandwidth cap), the data and WAL/redo layout, filesystem, and whether it is managed.
- Write profile: rows/s, row width, indexes per table, transaction size, commit rate, durability requirements (`synchronous_commit`, `innodb_flush_log_at_trx_commit`).

**Read-only.** Measure; never change `fsync`, flush settings, or storage on a live system from this skill — recommend, owner applies.

## Procedure

1. **Convert the symptom to bytes.** IOPS × IO size = throughput, and either number can be the cap. Many small random reads (index/heap lookups) hit the IOPS limit; large scans hit the throughput limit. Compare each to the *provisioned* ceiling, not the device's marketing peak.
2. **Reads — shrink what must come from disk:**
   - **Working set vs memory.** If hot data fits in cache, reads are mostly hits; a low hit ratio with a growing `blks_read` means the working set outgrew RAM or a scan is evicting it. Fix order: stop the scan (index, predicate, partition pruning), then shrink the data (narrower rows, drop dead indexes, compress, archive cold rows — `polymath-database:data-retention-archiving`), then add memory.
   - **Read amplification.** Rows examined ≫ rows returned; heap fetches per index hit; low index correlation turning an index range scan into random IO; `SELECT *` pulling wide/TOASTed columns that are discarded. Narrow the projection, add covering columns for hot reads, cluster/partition by the common filter.
   - **Table/index bloat.** Dead space makes every scan read more pages. Measure (`pgstattuple`, `pg_stat_user_tables.n_dead_tup`); fix the cause (autovacuum lag, long transactions pinning the horizon, update-heavy rows) before `pg_repack` or rebuilds.
3. **Writes — shrink what must be made durable:**
   - **Write amplification.** One logical row write becomes heap + every index + WAL (+ full-page images after a checkpoint) + replica traffic. Fewer indexes, narrower rows, HOT-friendly updates (don't update indexed columns; leave `fillfactor` headroom), and not rewriting unchanged values all cut it.
   - **Commit path.** Each commit waits for a log flush. Group commit helps concurrent writers; batching many rows per transaction (hundreds–thousands, not millions) cuts fsyncs by orders of magnitude. Relaxing durability (`synchronous_commit = off`, `innodb_flush_log_at_trx_commit = 2`) trades up to a few hundred ms of recent commits on crash for latency — a business decision, never a default; never `fsync = off`.
   - **Checkpoints.** Too-frequent checkpoints (small `max_wal_size` / redo log) cause write bursts and full-page-image storms; too-rare ones lengthen crash recovery. Check requested-vs-timed checkpoints, spread writes (`checkpoint_completion_target`), and size WAL/redo to the write rate.
   - **Bulk loads.** Use `COPY` / multi-row inserts / `LOAD DATA`, drop or defer secondary indexes for the load when feasible, load in sort order, and avoid per-row round trips.
4. **Storage layout and limits.** Separate WAL/redo from data when the volume class or latency profile warrants; know the volume's IOPS/throughput/burst model (a burst balance that drains produces a cliff, not a slope); check the instance's EBS/network bandwidth cap, filesystem (XFS/ext4 options), and read-ahead for scan-heavy engines. Prefer provisioning to the measured peak plus headroom over "bigger disk".
5. **Temp and spill IO.** Sorts/hashes spilling past `work_mem` (Postgres `temp_blks_written`, MySQL `Created_tmp_disk_tables`) are avoidable IO — fix the query or raise the per-session limit for that job, not the global default.
6. **Rank the changes by bytes saved per unit of risk**, apply one at a time, and re-measure the same IO metrics. State the expected effect as a measured delta to confirm, not a promised percentage.

## Output

```text
DB IO review: events-db (Postgres 15, 16 vCPU / 128 GB, gp3 12k IOPS / 500 MB/s)

Evidence
  reads   9.8k IOPS avg, 11.7k peak (98% of 12k) · cache hit 91% (was 99.4% last month) · working set ≈ 190 GB vs 96 GB shared_buffers + page cache
  writes  2.1k IOPS · WAL 38 MB/s · 74% of checkpoints requested (max_wal_size 4 GB) · commit p99 18 ms
  bloat   events_raw 41% dead/free space (long-running report held xmin 6 h)

Findings (ranked by bytes saved ÷ risk)
  1. Seq scan from nightly export reads 140 GB and evicts the hot set → add created_at partition pruning (see partitioning-sharding); run on a replica.
  2. events_raw bloat inflates every scan ~1.7× → fix the 6 h report transaction first, then pg_repack off-peak.
  3. Checkpoints requested 74% → raise max_wal_size to 32 GB; expect fewer full-page images (verify pg_stat_wal.wal_fpi).
  4. 7 indexes on a 2.1k writes/s table; 2 unused → each removed index cuts heap+WAL writes (see index-strategy).
Not changed: synchronous_commit stays on (payments data — durability is a business requirement).
Verify after each change: IOPS vs ceiling, cache hit, wal_fpi/s, checkpoint ratio, commit p99.
Unknowns: [TBD: whether the volume has burst credits — IOPS held at 12k for 6 h suggests provisioned, confirm in the volume metrics].
```

## Quality bar

- IO is expressed as IOPS, throughput, and latency against provisioned ceilings, not "high disk usage".
- Each recommendation reduces bytes read or written (or fsyncs), and says which metric will show it.
- Durability trade-offs are named as business decisions with the failure window stated; none are slipped in as a "free" tweak.
- Bloat is traced to its cause before a rebuild is proposed.
- Findings are ordered by impact per risk and applied one at a time.

## Anti-patterns to avoid

- Buying provisioned IOPS before finding the scan or missing index generating them.
- Turning off `fsync` / `full_page_writes`, or setting relaxed commit globally, to win a benchmark.
- `VACUUM FULL` or an unthrottled rebuild on a hot table during peak.
- Huge transactions (millions of rows) as "batching" — they bloat, block vacuum, and lag replicas; batch in bounded chunks.
- Benchmarking on a data set that fits in RAM and extrapolating to one that doesn't.
- Treating cache hit ratio as a goal: 99% can hide a hot scan, and 90% can be fine for a cold archive table.
