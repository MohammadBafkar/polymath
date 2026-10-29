# polymath-streaming

Data & streaming engineering craft for the Polymath marketplace. The engineering
side of data — distinct from `polymath-data` (analytics: SQL, experiments, metrics).
Pairs with `polymath-architecture:event-driven-design` for the business event flow.

## What it ships

- Skills:
  - `streaming-design` — Kafka/Pulsar/Kinesis topology: topics, partition key, delivery semantics, consumer groups, retention/compaction, backpressure, DLQ.
  - `data-pipeline` — ETL vs ELT, batch vs streaming, orchestration DAG, idempotent backfills, schema-drift handling, data-quality gates, lineage.
  - `data-modeling` — dimensional (star/snowflake) vs normalized vs lakehouse medallion, fact grain, conformed dimensions + SCD, partitioning, schema evolution.
  - `stream-processing` — windowing (tumbling/sliding/session), watermarks + late data, bounded state, exactly-once, stream joins, CEP, reprocessing.
  - `kafka-performance-tuning` — producer batching/compression/acks, consumer fetch and rebalances, lag diagnosis, broker IO and replication.
  - `azure-event-hubs-design` — tier and throughput-unit sizing, partitions, consumer groups, checkpointing, Capture to the lake, Kafka endpoint, geo-DR.
  - `lakehouse-performance` — Databricks/Spark and Delta: small files, OPTIMIZE and clustering, shuffle and skew, MERGE, Auto Loader, streaming triggers, cost.
  - `data-lake-layout` — zones and paths, Parquet and Delta/Iceberg/Hudi, file sizing, partitioning, compaction, lifecycle tiers, access control.
  - `event-schema-evolution` — registry compatibility modes, upgrade order, expand/migrate/contract for breaking changes, CI contract checks.

Retention and archiving across events, databases, and lakes: `polymath-database:data-retention-archiving`.

## Installation

```bash
claude plugin install polymath-streaming@polymath
```

## Dependencies

- `polymath-core`
- `polymath-data`

## License

MIT.
