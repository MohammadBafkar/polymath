---
name: db-scaling-strategy
description: Choose how to scale a database, cheapest first — tune, cache, replicas, partition, shard, CQRS. Not shard-key design.
---

# db-scaling-strategy

> Scale the database in the order of reversibility and cost: remove waste, then add copies, then split — and only split when the numbers say you must. Sharding is the last rung, not the first.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- The primary is approaching a limit (CPU, IOPS, connections, storage, write throughput) and growth continues.
- Someone proposes sharding, a NoSQL migration, or "a bigger instance" and you need the decision framed with evidence.
- Planning the database half of a scalability design (`polymath-scalability:system-design`).

Not this when: the bottleneck isn't identified — run `polymath-database:db-performance-triage` first. Choosing the shard/partition key itself is `polymath-database:partitioning-sharding`; non-relational key design is `polymath-database:nosql-partition-design`.

## Inputs

- Which resource is the limit and its measured headroom (from triage or `polymath-sre:capacity-plan`); growth rate and horizon (12–24 months).
- Read/write split, peak QPS and rows/s, data size and growth, hot-set size, latency SLO, consistency needs (what may be stale, for how long).
- Engine, managed service limits (max instance size, max replicas, storage caps), team operating capacity, budget.

## Procedure

Climb the ladder; at each rung state the trigger to move up, what it buys, and what it costs to undo.

1. **Remove waste (rung 0).** Missing indexes, N+1s, chatty ORMs, unbounded queries, bloat, oversized rows, unneeded history. Often a 2–10× headroom gain at zero architectural cost. Triage evidence required before climbing.
2. **Pool and cap concurrency.** A pooler (PgBouncer, ProxySQL, RDS Proxy) and an app-side concurrency limit stop connection thrash; tail latency usually improves before throughput does.
3. **Cache reads (rung 1).** If reads dominate and tolerate staleness, a cache absorbs the hot set — `polymath-performance:caching-tradeoffs`. Cost: invalidation correctness and a second failure mode.
4. **Scale up (rung 2).** Bigger instance, faster storage. Cheap, reversible-ish, no code change; bounded by the largest instance and rising price curve. It buys time — name how long (headroom date).
5. **Read replicas (rung 3).** Offload reads that tolerate replication lag; route by query class, not randomly. Costs: lag (read-your-writes breaks — pin a session to the primary after a write, or use `session LSN`/GTID waits), replica-conflict cancellations, and it does nothing for write throughput. Max replica count and fan-out cost apply.
6. **Functional split and archive (rung 4).** Move cold data out (`polymath-database:data-retention-archiving`), split independent domains into separate databases (aligns with service boundaries — `polymath-architecture:service-decomposition`), and move analytics off the OLTP primary (replica, CDC into a warehouse/lake).
7. **Partition tables (rung 5).** Declarative partitioning inside one node: pruning, cheap retention, smaller indexes. Doesn't add write capacity beyond the node.
8. **CQRS / specialized read models (rung 6).** Maintain a search index, wide-column store, or materialized read model fed by events/CDC for read patterns the primary can't serve. Costs: eventual consistency, rebuild path, dual-write avoidance (outbox — `polymath-architecture:event-driven-design`).
9. **Shard (rung 7).** Only when single-writer throughput or data size exceeds what rungs 0–6 can deliver for the planning horizon. Costs are permanent: cross-shard queries and transactions, resharding, operational tooling, hot-shard risk. Decide the key in `polymath-database:partitioning-sharding`; consider a natively distributed engine (CockroachDB, Spanner, Aurora Limitless, Vitess, Citus) before hand-rolled sharding.
10. **Polyglot (parallel rung).** Move a workload to an engine shaped for it (time-series, search, wide-column, key-value) when its access pattern is the mismatch — not because the relational DB is "slow" on an unindexed query.
11. **Write the decision.** Chosen rung, the measured trigger that forced it, the next trigger (a number and a date from headroom projection), the rollback cost, and who operates it. Record via `polymath-writing:adr` for the big steps.

## Output

```text
DB scaling decision: payments-db (Postgres 15, primary db.r6g.4xlarge)

Limit: write IOPS 71% of provisioned at peak; storage 4.1 TB growing ~220 GB/mo; reads 82% of QPS.
Headroom (polymath-sre:capacity-plan): write ceiling at 70% hit in ~7 months; storage in ~16 months [VERIFY: growth fit].

Ladder
  0 waste        done — removed 3 unused indexes, fixed 2 N+1s (−18% write IOPS)
  1 cache        ADOPT — 14k reads/s are profile/limits lookups, staleness ≤ 30 s ok
  3 read replica ADOPT — reporting + order-history reads; session-pinned after writes
  4 archive      ADOPT — move payments > 18 months to cold storage (≈ 55% of data)
  2 scale up     RESERVE — next step when write IOPS > 70% sustained (cost [TBD: price delta])
  5 partition    ADOPT — ledger_entries by month; retention by detach
  7 shard        DEFER — trigger: single-primary write ceiling inside 6 months after the above; evaluate Citus/Aurora Limitless first
Rejected: NoSQL migration — access patterns are relational (joins across ledger/accounts), no evidence the engine is the limit.

Next review trigger: write IOPS > 70% sustained 10 min, or storage > 70% of cap.
Rollback cost: replicas/cache low; partitioning medium (rewrite); sharding very high.
Owner: platform-db team. Unknowns: [TBD: managed-service max replica count and cross-region lag SLO].
```

## Quality bar

- Each rung adopted or skipped carries the measured reason; sharding is justified against the lower rungs, not asserted.
- The decision includes the next trigger as a number and the cost of undoing the choice.
- Read-your-writes and staleness consequences of replicas/caches are stated and handled.
- The write path and the read path are scaled separately — replicas and caches don't fix write limits.
- Operating cost (team, tooling, on-call) is part of the trade-off, not only instance price.

## Anti-patterns to avoid

- Sharding (or a rewrite to NoSQL) before eliminating waste and trying replicas, caching, partitioning, and archiving.
- Adding replicas for a write-bound system.
- Scaling up silently as the permanent answer with no headroom date.
- Random read routing that breaks read-your-writes.
- Choosing a shard key from the current schema instead of the access pattern.
- Dual-writing to a new store without an outbox or CDC.
