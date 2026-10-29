---
name: partitioning-sharding
description: Design table partitioning and shard keys — pruning, hot shards, cross-shard queries, resharding. Not whether to shard.
---

# partitioning-sharding

> The partition key is the schema's most expensive decision: it fixes which queries are cheap, which are scatter-gather, and which shards run hot. Choose it from the access pattern, and plan how you'll change it.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A large table needs partitioning for pruning, cheap retention, or manageable maintenance.
- `polymath-database:db-scaling-strategy` concluded sharding is required and you must pick the key, scheme, and routing.
- A shard is running hot, or a reshard/split is being planned.

Not this when: you haven't established that partitioning/sharding is needed — `polymath-database:db-scaling-strategy`. Key-value/wide-column stores (DynamoDB, Cassandra, Cosmos) have their own model — `polymath-database:nosql-partition-design`.

## Inputs

- The dominant queries and transactions with frequency: which filter by what key, which span entities, which are range scans.
- Data volume and growth, row/entity cardinality, and the distribution of the candidate key (top-N skew, largest tenant, hot entities).
- Retention rules, consistency needs (cross-entity transactions, unique constraints, foreign keys), engine and its partitioning features.
- Operational constraints: online migration tolerance, tooling, resharding appetite.

## Procedure

**A. Single-node partitioning (one database, many partitions)**

1. **Pick the purpose** — pruning (queries bound on the key), retention (drop a partition instead of `DELETE`), maintenance (smaller vacuum/index/backup units), or load spreading. If none apply, don't partition.
2. **Pick the key and method.** Range on time for event/log/ledger data (the usual winner — appends hit the newest partition, old ones detach); list for a small fixed set (region, tenant tier); hash for even spread when there is no natural range and point lookups dominate. The key must appear in the hot queries' `WHERE`, or pruning never fires.
3. **Size partitions** so each is a manageable unit — enough rows to amortize overhead, few enough that planning stays fast (hundreds, not tens of thousands). Daily partitions on a low-volume table are waste; a monolithic monthly partition on a billion-row-a-day table is not enough.
4. **Handle the constraints.** Unique and primary keys usually must include the partition key; foreign keys to/from partitioned tables have engine-specific limits; global secondary indexes may not exist (Postgres has none — every index is per partition). Say what is lost.
5. **Automate the lifecycle**: pre-create future partitions, attach/detach/drop on schedule (`pg_partman`, native `ALTER TABLE … DETACH PARTITION [CONCURRENTLY]`, MySQL `EXCHANGE PARTITION`), a default partition or alert for out-of-range rows, and a runbook for backfills.

**B. Sharding (many databases/nodes)**

6. **Pick the shard key from the access pattern.** Most OLTP systems shard by tenant, account, or entity id so a request touches one shard. Test candidates against: (a) request locality — % of requests/transactions resolvable on a single shard (target ≈ 95%+ for the hot paths), (b) distribution — no entity or tenant above a stated fraction of load (check the top-10 skew from real data), (c) growth — doesn't concentrate new writes on one shard (monotonic keys on range shards), (d) immutability — a key that changes means moving the row.
7. **Pick the scheme.**
   - **Hash** (consistent hashing or hash slots) — even spread, loses range scans on the key.
   - **Range** — keeps order and range queries; prone to hot tail shards for time/monotonic keys.
   - **Directory / lookup table** — flexible placement (move a big tenant alone), costs a lookup and its availability; cache it.
   - **Many logical shards on few physical nodes** (e.g. 1,024 logical shards mapped to 8 nodes) — resharding becomes moving shards, not re-hashing rows. Default to this.
8. **Deal with the cross-shard reality.** Queries without the key become scatter-gather (latency = slowest shard; cost grows with shard count): serve them from a secondary read model, search index, or warehouse instead. Cross-shard transactions: avoid by design; otherwise sagas/outbox (`polymath-architecture:distributed-consistency`), never ad hoc two-phase commit without a clear owner. Global uniqueness needs a coordinated id scheme (ULID/snowflake, or a per-shard prefix) or a global lookup. Reference/dimension tables are replicated to every shard.
9. **Plan the hot-shard response**: detect (per-shard QPS/latency/size dashboards), isolate a whale tenant to its own shard (directory scheme), split a shard (online copy + dual-write/CDC + cutover), or salt a hot key (at the cost of fan-out reads).
10. **Plan resharding before launch**: how data moves online (CDC/logical replication + backfill + verification + cutover + rollback), who routes (app library vs proxy such as Vitess, or the distributed engine), and the verification checksum. A sharding design without a resharding story is incomplete.
11. **Migration path** from the unsharded system: shadow-read/dual-write phases, a routing flag, per-tenant cutover, rollback criteria — `polymath-backend:migration-plan`.

## Output

```text
Partitioning/sharding design: ledger_entries (4.2 B rows, +30 M/day)

Stage A — partition (single node)
  Purpose: retention + pruning. Key: posted_at, RANGE monthly (≈ 900 M rows/month → [VERIFY: check partition size vs RAM; consider weekly]).
  PK becomes (id, posted_at) — unique id enforced via ULID generation; FK entries→accounts kept (account side unpartitioned).
  Lifecycle: pg_partman pre-creates 3 months; detach+archive > 24 months; DEFAULT partition + alert on any row.
  Expected: hot queries (account_id, posted_at range) prune to ≤ 2 partitions — confirm with EXPLAIN.

Stage B — shard (trigger: write ceiling inside 6 months, see db-scaling-strategy)
  Key: account_id. Single-shard requests: 97% (transfers between accounts on different shards = 3% → saga with outbox).
  Skew: top account = 0.8% of writes; no whale tenant [VERIFY: re-check quarterly].
  Scheme: 1,024 logical shards (hash(account_id) mod 1024) → 8 nodes; directory table maps logical → node (cached 60 s).
  Cross-shard: reporting via CDC → warehouse; global entry id = ULID; accounts/currencies tables replicated to all nodes.
  Hot shard: per-shard dashboards; move logical shards between nodes online (logical replication + checksum + cutover).
  Reshard: add nodes, move logical shards — no rehash. Rollback: keep source shard read-only 7 days.
  Migration: shadow reads → dual write → per-account cutover flag → decommission. Owner: platform-db.
```

## Quality bar

- The key is justified against locality, distribution (with measured skew), growth, and immutability — not by name.
- Cross-shard queries, transactions, and unique constraints each have an explicit answer.
- Resharding and hot-shard handling are designed up front, with the logical-shard indirection or equivalent.
- Partition counts and sizes are stated and checked against planning/maintenance cost.
- Anything dependent on the data's real distribution is marked `[VERIFY]` until measured.

## Anti-patterns to avoid

- Partitioning on a column the queries don't filter by.
- A monotonic key (auto-increment, timestamp) as a range shard key — all writes land on the last shard.
- `hash(key) mod N` with N physical nodes, making every resharding a full rewrite.
- Sharding by `user_id` when the dominant access is by `organization_id` — every request fans out.
- Cross-shard joins in the request path; two-phase commit across shards as the default.
- Launching a sharded system with no per-shard visibility and no resharding runbook.
