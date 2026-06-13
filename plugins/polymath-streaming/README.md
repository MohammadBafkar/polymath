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

## Installation

```bash
claude plugin install polymath-streaming@polymath
```

## Dependencies

- `polymath-core`
- `polymath-data`

## License

MIT.
