---
name: data-pipeline
description: Design a data pipeline — ETL vs ELT, batch vs streaming, orchestration/DAG, idempotent backfills, schema handling, data-quality checks, and lineage.
---

# data-pipeline

> A pipeline that can't be safely re-run is a pipeline that will eventually corrupt your warehouse. Design idempotency and backfill before you design transforms.

## When to use

- Building or reworking ingestion/transformation from sources into a warehouse/lake.
- A pipeline is non-idempotent, hard to backfill, or silently dropping/duplicating rows.
- A workflow invokes `polymath-streaming:data-pipeline`.

Not this when: you are choosing the target table shape — that is `polymath-streaming:data-modeling`. For the streaming transport itself, `polymath-streaming:streaming-design`. For analytic query tuning, `polymath-data:sql-optimize`.

## Inputs

- Sources (DBs, events, files, APIs), volumes, freshness SLA, and destination.
- Whether late/out-of-order or corrected data arrives.

## Procedure

1. **ETL vs ELT**: prefer ELT (load raw, transform in-warehouse) when the destination is a modern warehouse/lake — it preserves raw data and makes transforms re-runnable; use ETL when you must transform/filter before landing (PII, cost). State the choice.
2. **Batch vs streaming** by the freshness SLA: batch (scheduled, simpler, cheaper) unless sub-minute freshness genuinely matters; micro-batch as the middle ground. Don't pay for streaming you don't need.
3. **Orchestration**: model as a DAG with explicit dependencies (Airflow/Dagster/etc.); each task is retryable and observable. Avoid hidden cron chains.
4. **Idempotency + backfill** — the core: design every step so re-running a window produces the same result (idempotent writes: upsert/merge on a key, or delete-insert per partition). A backfill for any date range must be a first-class, safe operation.
5. **Schema handling**: validate on ingest; decide schema-on-read vs schema-on-write; version schemas and handle drift (new/removed/renamed columns) without breaking downstream.
6. **Data quality**: assertions at boundaries (row counts, null/range/uniqueness, referential checks); fail or quarantine on violation rather than propagating bad data.
7. **Late/out-of-order data**: define the lateness window and the correction strategy (reprocess affected partitions).
8. **Lineage + observability**: track source→table lineage, freshness, and volume; alert on staleness and anomalies.

## Output

- A one-page design: ETL/ELT + batch/streaming decisions, the DAG with retry/idempotency per step, the backfill procedure, schema-drift handling, the data-quality assertions + on-failure behavior, and lineage/freshness monitoring.

## Quality bar

- Every step is idempotent; re-running a window is safe and produces identical output.
- Backfill of an arbitrary range is a defined, first-class operation.
- Data-quality assertions gate the boundaries; violations quarantine, not propagate.
- Batch-vs-streaming is justified by the freshness SLA, not fashion.
