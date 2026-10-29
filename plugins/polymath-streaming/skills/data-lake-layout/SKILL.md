---
name: data-lake-layout
description: Design the physical data lake — zones, paths, Parquet and Delta/Iceberg, file sizing, partitioning, compaction, lifecycle tiers.
---

# data-lake-layout

> A lake's performance and cost are decided by its physical layout: how many files, how big, how partitioned, which table format, and where cold data lives. The logical model sits on top of this, so get the foundation right.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Standing up a data lake / lakehouse on S3, ADLS Gen2, or GCS, or restructuring one that is slow, costly, or a swamp.
- Choosing file and table formats, partition scheme, and compaction/lifecycle policies.
- Event streams (Kafka, Event Hubs Capture) land in the lake and need a sustainable layout and retention.

Not this when: you are modeling the data (grain, dimensions, medallion semantics) — `polymath-streaming:data-modeling`; tuning Spark/Databricks jobs — `polymath-streaming:lakehouse-performance`; building the pipelines — `data-pipeline`.

## Inputs

- Sources and arrival pattern (batch files, CDC, streams), daily volume and growth, number of tables/datasets.
- Query patterns: engines (Spark, Trino/Athena, Synapse/Fabric, Snowflake external, DuckDB), common filters and joins, freshness and latency needs.
- Governance: PII, access boundaries by domain/team, retention/legal rules (`polymath-database:data-retention-archiving`), and cloud/provider constraints.

## Procedure

1. **Define zones and ownership**: raw/bronze (immutable landing, source format preserved), cleaned/silver (conformed, deduplicated, typed), curated/gold (business aggregates, marts), plus a quarantine area for bad records and a scratch area with expiry. One owner per dataset; separate storage accounts/buckets (or at least containers/prefixes with distinct policies) for zones with different access, retention, or encryption.
2. **Choose the path convention** and keep it stable: `/{zone}/{domain}/{dataset}/…` with partition folders only where partitioning is intended. Lowercase, no spaces, no PII in paths. Never encode schema version or environment inconsistently. Avoid deep nesting that inflates listing cost.
3. **Choose file formats by role**: Parquet (columnar, compressed, predicate pushdown) as the default for analytics; ORC where the ecosystem favors it; Avro for row-oriented landing of streams and schema-carrying exchange; JSON/CSV only as raw landing, never as the query format. Compression: Snappy (fast) or ZSTD (better ratio, widely supported now) — pick one and measure.
4. **Choose a table format** for anything updated, deleted, or queried concurrently: **Delta Lake**, **Apache Iceberg**, or **Apache Hudi** give ACID commits, schema evolution, time travel, and efficient upserts/deletes over files. Decide by ecosystem and engines (Databricks → Delta; multi-engine/open catalog → Iceberg; some streaming-upsert patterns → Hudi), catalog (Unity Catalog, Glue, Hive Metastore, Polaris/REST catalogs), and governance. Raw append-only landing can stay plain files. Avoid mixing formats ad hoc across zones.
5. **Size files deliberately.** Target roughly 128 MB–1 GB per Parquet file (row groups of ~128 MB). Too many small files cost: metadata listing, per-file open overhead, and task scheduling; too-large files hurt parallelism and rewrite cost. Streaming and frequent micro-batches produce tiny files → plan **compaction** (table-format `OPTIMIZE`/`rewrite_data_files`) and write-time batching.
6. **Partition sparingly.** Partition by a low-cardinality column used in most filters (usually event date), only when the table is large enough that each partition holds hundreds of MB to GBs. Prefer table-format features (Iceberg hidden partitioning and partition evolution, Delta liquid clustering) to rigid hive-style folders. Partition by event date, not ingestion date, when queries filter by event time — or keep both with a plan for late data. Over-partitioning is the top cause of slow lakes.
7. **Mind object-store behavior**: request rates are per prefix and throttle (S3 supports high per-prefix request rates but extreme parallelism on one prefix can still 503; ADLS has account/partition limits) — spread hot writes across prefixes when needed; listing is slow and billed — rely on table-format metadata and catalogs rather than `ls`; renames on object stores aren't atomic (use committers/table formats); strongly consistent now on major clouds, but design commit protocols anyway.
8. **Lifecycle and cost**: tier by age and access (hot → cool/IA → archive) with rules per prefix; consider minimum storage durations and retrieval fees; expire scratch and staging; table-format maintenance (`VACUUM`, `expire_snapshots`, remove orphan files) to reclaim storage — coordinate with time-travel needs; compact before archiving. Replication/versioning on raw only if needed.
9. **Schema and quality at the boundary**: schema-on-write for silver+ (enforce types, nullability), schema evolution policy per table (`event-schema-evolution` for upstream contracts), quarantine invalid rows with the reason, and keep lineage/metadata (dataset descriptions, owners, freshness) in a catalog.
10. **Security**: least-privilege access by zone/domain (RBAC/ACLs on containers or prefixes, IAM policies), encryption at rest with managed keys, column/row-level security through the catalog/engine, masked or tokenized PII in silver/gold, audit logs; deletion requests via table-format `DELETE`/`MERGE` followed by `VACUUM`/snapshot expiry and backup aging.
11. **Prove it**: measure files per table and average size, bytes scanned per query, listing time, compaction lag, storage by tier, and cost per TB-month and per query; set alerts on small-file ratio and failed compaction.

## Output

```text
Data lake layout: retail analytics on ADLS Gen2 (Delta Lake, Unity Catalog)

Zones (one storage account each): raw / silver / gold ; plus quarantine + scratch (7 d expiry)
Paths: abfss://silver@lake/sales/orders/ (Delta) — no partition folders; liquid clustering (order_date, store_id)
Formats: raw — Avro (Event Hubs Capture) & CSV as delivered, immutable; bronze/silver/gold — Delta (Parquet + ZSTD)
Table format: Delta (Databricks primary; Iceberg UniForm for Trino readers) [VERIFY: engine matrix]
File sizing: target ≈ 256 MB–1 GB; auto compaction + predictive optimization; Capture files (5 min windows) compacted hourly into bronze
Partitioning: gold.daily_sales by sale_date (1.2 GB/day → fine); everything else clustered, not partitioned
Object-store: 8 hash-prefixed landing folders for the telemetry feed (throttle avoidance) [VERIFY: only if 503s]; no ls-based discovery (catalog only)
Lifecycle: raw → cool at 30 d, archive at 365 d; silver/gold hot; VACUUM 7 d; snapshots 30 d; scratch 7 d
Quality: schema enforcement at silver; quarantine table with reason code; owners/descriptions in the catalog
Security: RBAC per domain on containers; PII columns masked in gold; CMK per zone; erasure via DELETE + VACUUM + 35 d backup aging
Health metrics: avg file size per table (> 128 MB), files per partition, compaction lag, bytes scanned per query, $ per TB-month
Open: [TBD: retention for raw clickstream — legal/product decision]
```

## Quality bar

- Zones, ownership, and access/retention boundaries are explicit and map to storage boundaries.
- File size and partitioning choices are stated with their targets and justified against table size and query filters.
- Mutable data uses a table format with a defined compaction and snapshot-expiry routine.
- Lifecycle tiers consider retrieval cost and minimum durations; erasure covers all copies.
- Health metrics make small-file and cost regressions visible.

## Anti-patterns to avoid

- Partitioning by high-cardinality or ingestion-time columns that queries don't use.
- Landing streams directly as thousands of tiny Parquet files with no compaction.
- Querying raw JSON/CSV in production dashboards.
- Using directory listing as a catalog, or renames as commits on object storage.
- A single flat bucket for raw, curated, and scratch data with one access policy.
- Archiving or deleting files that table metadata still references (corrupting the table).
