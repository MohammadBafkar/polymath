# polymath-database

Database performance craft for the Polymath marketplace — engine-agnostic first, with one Postgres-specific skill.

## What it ships

- Skills:
  - `db-performance-triage` — top-down triage of a slow or saturated database (workload, waits, plans, IO, locks, pools) to ONE bottleneck. Ships a per-engine diagnostics reference.
  - `index-strategy` — design or prune indexes from the real workload: composite order, covering, partial, expression, index type, write cost, unused cleanup.
  - `db-io-tuning` — reduce read/write IO: working set vs cache, read/write amplification, WAL/fsync, checkpoints, bloat, volume IOPS limits.
  - `postgres-performance` — Postgres runtime tuning: `pg_stat_statements`, wait events, vacuum/bloat/HOT, index types, partitioning, pooling, locks, replicas. Ships a catalog-query reference.
  - `db-scaling-strategy` — the scaling ladder, cheapest first: tune, cache, scale up, replicas, archive, partition, CQRS, shard.
  - `partitioning-sharding` — table partitioning and shard-key design: pruning, hot shards, cross-shard queries, resharding.
  - `nosql-partition-design` — DynamoDB / Cassandra / Cosmos DB / MongoDB access patterns, partition keys, hot partitions, throughput.
  - `data-retention-archiving` — retention classes, hot/warm/cold tiers, partition-drop purges, legal hold, deletion propagation, restore tests (databases, event logs, lakes).

Related skills elsewhere: `polymath-data:sql-optimize` (reading one plan), `polymath-backend:audit-pg-config` (Postgres server settings), `polymath-backend:migration-plan` (shipping an index online), `polymath-performance:caching-tradeoffs`.

## Installation

```bash
claude plugin install polymath-database@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
