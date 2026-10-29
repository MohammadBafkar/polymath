---
name: lakehouse-performance
description: Tune Databricks/Spark and Delta — small files, OPTIMIZE, clustering, shuffle, skew, Auto Loader, cluster cost. Not lake layout.
---

# lakehouse-performance

> Lakehouse jobs are slow for three reasons: too many small files, too much data shuffled, or one skewed task holding the stage. Read the Spark UI first; tune the table layout before the cluster.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A Databricks/Spark job or SQL warehouse query is slow or expensive; the Spark UI shows spill, skew, or thousands of tiny tasks.
- Delta tables degrade over time (many small files, slow MERGE, slow reads); designing table maintenance.
- Setting up ingestion (Auto Loader) or Structured Streaming into Delta with predictable latency and cost.

Not this when: you are choosing the physical lake layout and file formats — `polymath-streaming:data-lake-layout`; the dimensional model — `data-modeling`; a single warehouse SQL query on Postgres-like engines — `polymath-data:sql-optimize`.

## Inputs

- The job/query, runtime (Databricks Runtime version, Photon on/off, serverless/classic), cluster size and type, and run history (duration trend, cost).
- Spark UI/query-profile evidence: stage/task time distribution (median vs max), shuffle read/write, spill (memory/disk), GC time, input file count and size, scan vs filter rows.
- Table facts: size, file count and average file size, partition columns and cardinality, clustering/Z-order columns, `DESCRIBE DETAIL` and `DESCRIBE HISTORY` output, write pattern (append, MERGE, streaming micro-batches).
- Feature availability depends on version/edition (liquid clustering, predictive optimization, deletion vectors, Photon) — verify for the workspace.

**Read-only first.** Inspect with `DESCRIBE DETAIL/HISTORY`, query profile, and Spark UI. `OPTIMIZE`, `VACUUM`, cluster resizing, and config changes are applied by the owner after review (`VACUUM` shortens time-travel and can break long-running readers).

## Procedure

1. **Establish where time goes** (Spark UI / query profile): per stage, compare task durations (median vs max ⇒ skew), shuffle read/write bytes, spill, GC%, task count, and input size vs rows. A stage with 50,000 tiny tasks is a small-files problem; one task 20× the median is skew; large spill is memory/partition sizing; a full scan with a selective filter is a layout/data-skipping problem.
2. **Fix the files and layout first (Delta):**
   - **Small files**: streaming and frequent appends create many KB-MB files. Enable optimized writes/auto compaction (or use predictive optimization on Unity Catalog managed tables), and schedule `OPTIMIZE` (target file size is typically hundreds of MB — let the platform defaults apply unless measured) for tables that are append-heavy.
   - **Data skipping**: Delta keeps min/max stats (by default on the first 32 columns); put filter and join columns early or set `delta.dataSkippingStatsColumns`/`dataSkippingNumIndexedCols`. Cluster data by the common predicate: **liquid clustering** (`CLUSTER BY`) for new tables — flexible and incremental — or `OPTIMIZE … ZORDER BY` on older tables (multi-column locality, rewrites more data). Don't also hive-partition the same column.
   - **Partitioning**: use hive-style partitions only for very large tables (multi-TB) on low-cardinality columns (date, region) with each partition holding ≥ ~1 GB; over-partitioning (by user_id, by hour on a small table) creates millions of small files and slow listings. Prefer clustering for most tables.
   - **Maintenance**: `VACUUM` to remove unreferenced files (retention default 7 days; keep ≥ the longest reader/stream lag and your time-travel need), and bound the transaction-log history. Deletion vectors speed `DELETE`/`UPDATE`/`MERGE` by avoiding full file rewrites (verify support).
3. **Fix the shuffle:**
   - Avoid it: broadcast the small side of a join (`broadcast()` hint or raise `spark.sql.autoBroadcastJoinThreshold` thoughtfully; AQE can convert at runtime); filter and project early; pre-aggregate; avoid `distinct`/`groupBy` on high-cardinality columns when a window or approximate function will do.
   - Size it: with AQE (default on) shuffle partitions coalesce automatically; if AQE is off or ineffective, set `spark.sql.shuffle.partitions` so each shuffle partition is ~100–200 MB (not the default 200 for a TB-scale shuffle).
   - **Skew**: confirm in the UI (max task ≫ median, one key dominating); enable AQE skew-join handling; salt hot keys or split hot keys into a separate broadcast/path; filter null/default keys that all hash together.
   - **Spill**: raise partitions (smaller tasks) or use memory-optimized instances before adding nodes; avoid collecting or caching huge DataFrames; prefer built-in functions/Photon over Python UDFs (serialization cost) — use pandas/Arrow UDFs if needed.
4. **MERGE/upsert performance**: include partition/cluster columns in the `ON` condition so the target files read are pruned (a MERGE without pruning rewrites the table); dedupe the source first (duplicate matches error out and waste time); keep batches reasonably large; use deletion vectors and Photon where available; for CDC use `foreachBatch` with MERGE and idempotency on a batch/version key.
5. **Ingestion**: use **Auto Loader** (`cloudFiles`) for incremental file ingestion — file-notification mode over directory listing at scale; define a schema or schema hints plus `schemaEvolutionMode`; `maxFilesPerTrigger`/`maxBytesPerTrigger` to bound batch size; quarantine bad records (`_rescued_data`). Land raw in bronze with minimal transformation, then incremental transforms downstream.
6. **Structured Streaming**: choose the trigger by the latency SLA — continuous micro-batches (`processingTime`) only when freshness demands; `availableNow` (incremental batch on a schedule) is far cheaper for hourly/daily freshness. Always set a checkpoint location (one per stream, never shared or deleted casually); bound state (watermark + TTL; RocksDB state store for large state); monitor input rate vs processing rate and batch duration vs trigger interval (if processing time ≥ interval, it falls behind). Design sinks idempotently (`foreachBatch` + MERGE, or Delta's exactly-once writes with checkpoint).
7. **Compute right-sizing**: pick instance families by bottleneck (memory-optimized for shuffle/spill-heavy, storage-optimized with local NVMe disk cache for repeated scans, compute-optimized for CPU-bound); enable Photon for SQL/DataFrame-heavy work if it pays off per job; autoscale with sensible min/max; use job clusters (or serverless) rather than all-purpose clusters for scheduled work; spot/preemptible for fault-tolerant jobs; avoid over-large clusters for jobs bounded by a single skewed task. Measure cost per run (DBUs + cloud), not just duration.
8. **Reduce the work**: read fewer columns/rows (column pruning, predicate pushdown into Parquet/Delta), compute incrementally (streaming tables/materialized views/incremental MERGE) instead of full refresh, cache only reused data, and retire unused tables (`polymath-database:data-retention-archiving`).
9. **Verify**: re-run on the same data volume; compare stage times, bytes scanned/shuffled/spilled, file counts, and cost per run; keep a baseline in the job's run history.

## Output

```text
Lakehouse performance review: silver.orders_enriched nightly job (DBR 15.4, Photon on, 16 × i3.2xlarge)

Symptom: 3 h 10 min (was 55 min in March); cost 3.4× [VERIFY: DBU + cloud].
Evidence
  Spark UI: stage 14 (MERGE into silver.orders) = 71% of runtime; 41,000 tasks, median 1.9 s, max 7 min (1 task)
  Table: DESCRIBE DETAIL → 380,000 files, avg 9 MB; partitioned by order_id (!); no OPTIMIZE in 90 d
  MERGE condition: t.order_id = s.order_id (no cluster/partition pruning on order_date)
  Skew: key "unknown_customer" = 11% of source rows
Diagnosis (ranked)
  1. Layout: partitioning on a high-cardinality column → 380k small files; MERGE scans all.
  2. MERGE without pruning predicate + skewed null-like key.
Changes
  1. Rewrite to CLUSTER BY (order_date, customer_id) [liquid clustering], drop order_id partitioning; run OPTIMIZE once; enable predictive optimization/auto compaction.
  2. MERGE ON t.order_date = s.order_date AND t.order_id = s.order_id (+ order_date range filter from source min/max); filter 'unknown_customer' to a side path.
  3. Job: availableNow incremental instead of full-day reprocess [VERIFY: source supports incremental watermark].
Expected: scan files from 380k to ≈ days-touched × files-per-day; runtime back near baseline — confirm on one night's run before the backfill.
Verify: files scanned in the MERGE, max/median task ratio < 3, spill 0, cost per run.
Not changed: cluster size (task skew, not capacity, is the limit).
Caution: VACUUM retention stays 7 d (downstream stream lags ≤ 2 d).
```

## Quality bar

- The diagnosis comes from Spark UI/Delta metadata evidence (task skew, file counts, bytes scanned/shuffled/spilled), not from a config list.
- Table layout and small files are addressed before cluster scaling; partition vs clustering choice is justified.
- MERGE/streaming recommendations preserve idempotency and checkpoints; `VACUUM`/retention changes consider time travel and long readers.
- Cost per run, not only duration, is the success metric.
- Version-dependent features are flagged `[VERIFY]`.

## Anti-patterns to avoid

- Scaling the cluster to fix skew or small files.
- Partitioning by high-cardinality columns, or `Z-ORDER` on columns that are also partition keys.
- `spark.sql.shuffle.partitions` copy-pasted values regardless of data size; disabling AQE without evidence.
- Python row-at-a-time UDFs in hot paths; `collect()` on large data.
- Sharing or deleting streaming checkpoints; running a 24/7 micro-batch stream for daily freshness.
- Setting `VACUUM` retention to 0 hours to "free space" while streams or readers lag.
