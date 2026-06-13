---
name: data-modeling
description: Model analytical data — dimensional (star/snowflake) vs normalized vs lakehouse medallion layers, grain, partitioning, slowly-changing dimensions, and schema evolution.
---

# data-modeling

> Declare the grain of every fact table in one sentence before you add a column. Most warehouse pain is a fact table whose grain nobody can state.

## When to use

- Designing warehouse/lake tables for analytics or as a pipeline's destination.
- Queries are slow/expensive or numbers disagree because the grain or layering is muddled.
- A workflow invokes `polymath-streaming:data-modeling`.

Not this when: you are designing an OLTP transactional schema for a service — that is `polymath-backend:db-schema`. For the pipeline that loads these tables, `polymath-streaming:data-pipeline`.

## Inputs

- The analytical questions/metrics to support and the source data.
- Volume, query patterns, and freshness.

## Procedure

1. **Choose the modeling style**:
   - *Dimensional (Kimball star)* — facts + denormalized dimensions; the default for BI/analytics, fast and understandable.
   - *Normalized (3NF/Inmon)* — an integration layer feeding marts; when many sources must reconcile.
   - *Lakehouse medallion* — bronze (raw) → silver (cleaned/conformed) → gold (aggregated/serving); the default on a lake. State which layer each table is.
2. **State the grain** of every fact table in one sentence ("one row per order line per day"). Everything else follows from the grain; mixed grain is the root defect.
3. **Facts vs dimensions**: facts are measurements at the grain (additive where possible); dimensions are descriptive context. Conform dimensions so they're shared across facts.
4. **Slowly-changing dimensions**: pick per dimension — Type 1 (overwrite), Type 2 (versioned history with effective dates), Type 3 (limited history). History needs drive the choice.
5. **Partitioning + clustering**: partition by the dominant filter (usually date) to prune scans; cluster/sort by frequent predicates. Name the partition column.
6. **Schema evolution**: additive-by-default; version breaking changes; keep raw/bronze immutable so you can rebuild silver/gold.
7. **Keys & late-arriving data**: surrogate keys for dimensions; handle late facts/early-arriving facts explicitly.

## Output

- A one-page model: chosen style + (for lakehouse) layer per table, the stated grain of each fact, conformed dimensions with SCD type, partition/cluster keys, and the schema-evolution rule.

## Quality bar

- Every fact table's grain is stated in one sentence and is uniform.
- Dimensions are conformed and each has an explicit SCD type.
- Tables are partitioned by the dominant filter to bound scan cost.
- Raw/bronze is immutable so downstream layers are rebuildable.
