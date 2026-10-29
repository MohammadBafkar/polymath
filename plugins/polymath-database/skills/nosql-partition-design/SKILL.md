---
name: nosql-partition-design
description: Design NoSQL access patterns and partition keys (DynamoDB, Cassandra, Cosmos, Mongo) — hot partitions, indexes, throughput, TTL.
---

# nosql-partition-design

> In key-value and wide-column stores you model the queries, not the entities. The partition key decides throughput ceiling, latency, and cost — and can't be changed without a migration.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Designing a DynamoDB / Cassandra / ScyllaDB / Cosmos DB / Bigtable / MongoDB data model.
- Throttling (`ProvisionedThroughputExceeded`, 429 / `RequestRateTooLarge`), a hot partition, large partitions, or runaway cost.
- Deciding whether a workload fits a NoSQL store at all.

Not this when: the store is relational and the question is sharding — `polymath-database:partitioning-sharding`. Index design in a relational engine — `polymath-database:index-strategy`.

## Inputs

- The access patterns, enumerated: each query/write with its key, frequency (per second at peak), latency target, result size, and consistency need.
- Entity sizes and relationships; cardinality and skew of candidate keys (top tenant, hottest item).
- The store, its capacity mode (on-demand vs provisioned throughput / RU/s), and its limits (item size, partition size, per-partition throughput) — check current documentation for the numbers; they change.

## Procedure

1. **List every access pattern first** (a table: pattern · key attributes · read/write · rate · latency). The model is derived from this list; a pattern not on it is not supported.
2. **Choose the partition key for distribution and locality.** It must (a) have high cardinality, (b) spread request *rate* and *data size* evenly — a key that is evenly populated can still be hot (a "today" key, a viral item, one big tenant), (c) be the equality predicate of the hot queries. A queries-by-partition-key read is a single-partition operation; anything else is a scan or fan-out.
3. **Choose the sort/clustering key** to make range reads and ordering free within a partition: time-ordered ids, composite sort keys that group related items so one `Query` returns an aggregate with its children (single-table design in DynamoDB; wide rows in Cassandra).
4. **Keep partitions bounded.** Unbounded growth (all events for a device forever) breaks per-partition size limits and read latency: bucket by time (`device#2025-10`), by hash suffix, or cap and roll over. Choose bucket size from measured volume, with a plan for readers to enumerate buckets.
5. **Spread hot keys deliberately.** Write sharding by appending a suffix (`item#0..N`) trades one hot partition for N reads to aggregate; cache or CDN hot reads (DAX / app cache) before sharding keys; queue and batch write bursts. Adaptive capacity helps imbalance, not a single hot key.
6. **Secondary access patterns.** Local/global secondary indexes (DynamoDB GSI/LSI), materialized views / SAI (Cassandra), partition-key-changing indexes (Cosmos). Each GSI is a second table: costs write throughput, is eventually consistent, and has its own hot-key risk — project only the attributes needed. Prefer a denormalized duplicate item written in the same transaction/batch over a join that doesn't exist.
7. **Denormalize with a consistency plan.** Duplicated data must be updated together (transactions where the store has them, otherwise idempotent writers + a repair job). Avoid read-modify-write races with conditional writes / optimistic version attributes / lightweight transactions only where required (LWTs and cross-partition transactions cost latency and throughput).
8. **Consistency and quorum.** Eventual vs strong reads (DynamoDB), tunable consistency (`LOCAL_QUORUM` vs `ONE`, Cosmos levels). State the choice per pattern and the multi-region implication.
9. **Capacity and cost.** Convert peak rates and item sizes into throughput units for the store (read/write capacity units or RU — use the vendor's current formula), add GSI write amplification, decide on-demand vs provisioned with autoscaling, and compute the per-partition share against the per-partition limit. Large items and scans are the usual cost surprise — project less, compress, or offload payloads to object storage with a pointer.
10. **Lifecycle.** TTL for expiring data (note: DynamoDB TTL deletion is asynchronous, doesn't consume write capacity, and still emits stream events; Cassandra TTL creates tombstones — mind `gc_grace_seconds` and time-window compaction), export/archive to the lake (`polymath-database:data-retention-archiving`), and a backup/point-in-time-recovery setting.
11. **Fit check.** If most patterns need ad hoc queries, joins, or multi-entity transactions, the access pattern is relational — say so and stop (`polymath-database:db-scaling-strategy`).

## Output

```text
NoSQL model: device telemetry + device registry (DynamoDB, on-demand → provisioned later)

Access patterns
  A1 get device profile                     pk=DEVICE#<id>, sk=PROFILE                    3k/s read   p99 < 10 ms
  A2 latest N readings for a device         pk=DEVICE#<id>#<yyyymm>, sk=TS#<iso>, rev     20k/s write 6k/s read
  A3 devices in a site                      GSI1 pk=SITE#<id>, sk=DEVICE#<id>              50/s read
  A4 all devices with open alert            sparse GSI2 pk=ALERT#open, sk=<site>#<id> + write-shard suffix (0–7)   5/s read
Keys
  Reading partitions bucketed per device-month: bounds partition size (≈ 21 MB/month at 1 reading/min × 0.5 KB [VERIFY: measured item size]); readers enumerate ≤ 2 buckets for "latest".
  Hot-key check: top device = 0.02% of writes; site GSI top site = 3% (acceptable) — [VERIFY quarterly].
Alerts index is sparse and write-sharded (8 suffixes) so one `ALERT#open` key can't throttle; A4 reads 8 keys in parallel.
Consistency: A1 strongly consistent read after registration; A2/A3 eventual.
Capacity: A2 20k writes/s × 0.5 KB items → [TBD: units from vendor formula] + GSI writes; per-partition write share ≈ 20k/(devices spread) — within limits because pk spreads across 120k devices.
Lifecycle: TTL 90 d on readings; nightly export to S3 (Parquet) for analytics; PITR on.
Rejected: single "readings" partition per site (hot, unbounded); scan for open alerts (cost).
```

## Quality bar

- Every access pattern has a key path; none is served by a scan unless explicitly accepted and costed.
- The partition key is checked for *rate* skew as well as data skew, with the hot-key mitigation named.
- Partition growth is bounded, and GSIs' costs and consistency are stated.
- Capacity is computed from rates and item sizes using the vendor's current formula, or marked `[TBD]`.
- Denormalized copies have a defined consistency mechanism.

## Anti-patterns to avoid

- Modeling entities first and discovering the queries later.
- A low-cardinality or time-only partition key (`status`, `date`) — one partition takes all the writes.
- Unbounded partitions (all history under one key) and giant items.
- Using scans or filter expressions as the query path; filters don't reduce read cost.
- A GSI/MV per ad hoc question — each one multiplies write cost and lag.
- Picking NoSQL to escape a missing relational index.
