---
name: db-performance-triage
description: Triage a slow or saturated database top-down (workload, waits, plans, IO, locks, pools) to ONE bottleneck. Engine-agnostic; not one query plan.
---

# db-performance-triage

> Don't tune what you haven't measured. Find which resource the database is actually starved of — CPU, IO, locks, memory, or connections — then fix that, not the query you happened to look at.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- "The database is slow", latency or CPU spiked, or the app times out waiting on queries and nobody knows which one.
- Before buying a bigger instance: prove the bottleneck is capacity and not a bad query, missing index, or lock.
- A workflow or review needs a ranked, evidence-backed cause — not a pile of tuning tips.

Not this when: you already have one slow query and its plan — that is `polymath-data:sql-optimize`. For Postgres-specific catalog queries and settings, continue with `polymath-database:postgres-performance` after this.

## Inputs

- Engine + version, instance size (vCPU, RAM, storage type and provisioned IOPS/throughput), and whether it is managed.
- The symptom with a time window: which endpoints, latency percentiles, error/timeout rate, and what changed (deploy, traffic, data growth, config).
- Access to workload statistics (see [references/diagnostics.md](references/diagnostics.md)): top-statements view, wait events, lock views, and host/volume metrics. Missing one → say which step it blocks and continue with the rest.

**Read-only.** Gather with `SELECT`/`SHOW`/metrics only. Never `KILL`, `VACUUM FULL`, `ALTER SYSTEM`, drop an index, or flush a cache on a live primary — recommend; the owner applies. `EXPLAIN ANALYZE` executes the query: use a replica or a rollback block.

## Procedure

Walk the layers in order (a USE-method pass — Utilization, Saturation, Errors — per resource). Stop at the first layer with decisive evidence, not the first plausible one.

1. **Frame the symptom.** One sentence: which queries/endpoints, which percentile, since when, correlated with what change. A regression with a start time is a diff problem; a slow climb is a growth problem. Different hunts.
2. **Host resources (USE).** CPU utilization + run-queue, memory + swap, disk IOPS / throughput / queue depth / latency vs the provisioned ceiling, network. A resource at its ceiling with a queue is the lead. Cloud volumes throttle silently at their IOPS/throughput caps — check the burst-credit or throttle metric, not just utilization.
3. **Connections.** Active vs idle vs idle-in-transaction, vs `max_connections`/pool size. Many active sessions on few cores is saturation (latency grows with every extra concurrent query); a wall of idle-in-transaction holds locks and snapshots. Fix with a pooler and a lower concurrency cap before touching queries.
4. **Where the time goes — waits.** Sample wait events (Postgres `pg_stat_activity.wait_event`, MySQL `performance_schema` waits, SQL Server `sys.dm_os_wait_stats`, Oracle ASH). Classify: CPU, IO read, IO write/WAL/fsync, lock, latch/LWLock, client (app is slow, not the DB). The dominant class decides the next step.
5. **Workload — which statements.** Rank by *total* time (`calls × mean`), not worst single run: `pg_stat_statements`, MySQL `events_statements_summary_by_digest`, SQL Server Query Store. Top 3–5 usually carry most of the load. Note calls/sec — a 2 ms query called 20k/s (an N+1) beats a 3 s report.
6. **Per-statement plan.** For the top statements only, read the plan (`polymath-data:sql-optimize`): rows scanned vs returned, estimate-vs-actual drift, sort/hash spills, nested-loop blowups, plan flips after stats change.
7. **Indexes and schema.** Missing (seq scan on a selective predicate), redundant/unused (write cost for no reads), wrong column order → `polymath-database:index-strategy`. Bloat and table width → `polymath-database:db-io-tuning`.
8. **Locks and contention.** Blocking chains, deadlock log, long transactions, hot rows (counters, queue tables, a single "latest" row), DDL waiting behind a long transaction.
9. **Maintenance and stats.** Stale statistics, vacuum/autovacuum lag, dead tuples, checkpoint storms, replica lag, long-running backups competing for IO.
10. **Decide: tune, or scale.** If the top statements are fixed-cost and the resource is genuinely saturated, the answer is capacity or architecture — `polymath-database:db-scaling-strategy`. If one fix would drop a resource below ~60–70% sustained, do that fix first.

## Output

```text
DB triage: orders-db (Postgres 16, db.r6g.2xlarge, 8 vCPU / 64 GB, gp3 6k IOPS) — checkout p99 0.4 s → 2.8 s since Tue 14:10

Symptom: POST /checkout p99 regression; started with deploy 2025.41 (adds order-history lookup).
Evidence by layer
  host      CPU 38% · IOPS 5.9k/6k (98% of provisioned, queue depth 14) · mem fine      ← IO saturated
  conns     active 22 / 120, idle-in-tx 0                                                 ← not it
  waits     61% IO:DataFileRead, 22% CPU, 4% Lock                                         ← read IO
  workload  #1 SELECT … FROM orders WHERE customer_id=$1 ORDER BY created_at DESC LIMIT 20
            41% of total time · 18k calls/s · mean 3.1 ms · shared_blks_read 96/call
  plan      Seq Scan on orders (rows removed by filter 99.98%) — no index on customer_id
Dominant bottleneck: read IO from a missing index on orders(customer_id, created_at DESC) (introduced by the new query).
Not the cause (checked): connections, locks, checkpoints, replica lag.
First fix (one change): CREATE INDEX CONCURRENTLY orders_customer_created_idx ON orders (customer_id, created_at DESC) — plan it with polymath-backend:migration-plan.
Verify: IOPS < 60% of provisioned, query mean < 0.3 ms, shared_blks_read/call < 5, checkout p99 back under 0.5 s.
Unknowns: [VERIFY: whether read replicas can absorb the order-history reads — would remove the load from the primary entirely].
```

## Quality bar

- ONE dominant bottleneck, with the layer's evidence — and the layers checked and ruled out are listed.
- Statements ranked by total time and calls/sec, not by slowest single execution.
- Every metric is read against the provisioned ceiling, not in isolation.
- The first fix is a single change with a measurable success criterion; "upgrade the instance" is only offered after the cheaper layers are eliminated.
- No live-system mutation was proposed as something the skill itself runs.

## Anti-patterns to avoid

- Starting from the config file or a favorite tuning parameter instead of the symptom.
- Optimizing the slowest query when a 2 ms query at 20k calls/s owns the load.
- Reading averages: a p99 problem hides in the tail, in waits, and in lock chains.
- Scaling up to mask a missing index — the bill grows, the problem returns at 2× traffic.
- Changing several things at once, so nobody knows what helped.
- Judging on a cold cache or a different data volume than production.
