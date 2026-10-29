# Changelog — polymath-database

<!-- markdownlint-disable MD024 -->

## [Unreleased]

New plugin: database performance craft.

### Skills

- **db-performance-triage** — Triage a slow or saturated database top-down (workload, waits, plans, IO, locks, pools) to ONE bottleneck. Engine-agnostic; not one query plan.
- **index-strategy** — Design or prune indexes from the query workload — column order, covering, partial, type, write cost, unused cleanup. Not plan reading.
- **db-io-tuning** — Cut database IO — cache and working set, read/write amplification, WAL/fsync, checkpoints, bloat, volume IOPS limits. Not plans or indexes.
- **postgres-performance** — Tune Postgres runtime performance — pg_stat_statements, vacuum/bloat/HOT, index types, locks, pooling. Not server config (audit-pg-config).
- **db-scaling-strategy** — Choose how to scale a database, cheapest first — tune, cache, replicas, partition, shard, CQRS. Not shard-key design.
- **partitioning-sharding** — Design table partitioning and shard keys — pruning, hot shards, cross-shard queries, resharding. Not whether to shard.
- **nosql-partition-design** — Design NoSQL access patterns and partition keys (DynamoDB, Cassandra, Cosmos, Mongo) — hot partitions, indexes, throughput, TTL.
- **data-retention-archiving** — Design retention and archiving — tiers, partition-drop purges, legal hold, deletion requests, restore tests — for DBs, event logs, lakes.
