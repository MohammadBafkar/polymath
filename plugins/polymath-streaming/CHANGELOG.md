# Changelog — polymath-streaming

<!-- markdownlint-disable MD024 -->

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
