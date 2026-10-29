# Changelog — polymath-streaming

<!-- markdownlint-disable MD024 -->

## [Unreleased]

### Added

- **kafka-performance-tuning** — Tune Kafka throughput, latency and consumer lag — producer batching, acks, fetch, rebalances, broker IO. Not topology (streaming-design).
- **azure-event-hubs-design** — Design and size Azure Event Hubs — tier, throughput units, partitions, consumer groups, checkpointing, Capture, Kafka endpoint.
- **lakehouse-performance** — Tune Databricks/Spark and Delta — small files, OPTIMIZE, clustering, shuffle, skew, Auto Loader, cluster cost. Not lake layout.
- **data-lake-layout** — Design the physical data lake — zones, paths, Parquet and Delta/Iceberg, file sizing, partitioning, compaction, lifecycle tiers.
- **event-schema-evolution** — Evolve event schemas safely — registry, Avro/Protobuf compatibility modes, upgrade order, breaking-change playbook, CI contract checks.

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 4 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- All four skills show an exact output shape; `streaming-design` sizes partitions with an explicit formula.

## [0.8.0]

Data & streaming engineering: streaming topology + delivery semantics, ETL/ELT pipelines, dimensional/lakehouse modeling, stream processing.

### Skills

- **data-modeling** — Model analytical data — dimensional (star/snowflake) vs normalized vs lakehouse medallion layers, grain, partitioning, slowly-changing dimensions, and schema evolution.
- **data-pipeline** — Design a data pipeline — ETL vs ELT, batch vs streaming, orchestration/DAG, idempotent backfills, schema handling, data-quality checks, and lineage.
- **stream-processing** — Design stream processing — windowing (tumbling/sliding/session), watermarks for late data, stateful operators, exactly-once, stream-stream/table joins, and CEP.
- **streaming-design** — Design a streaming topology (Kafka/Pulsar/Kinesis) — topics, partitioning key, delivery semantics, consumer groups, retention/compaction, ordering, and backpressure.
