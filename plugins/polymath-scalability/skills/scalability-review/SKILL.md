---
name: scalability-review
description: Review an architecture for scale bottlenecks — single writers, shared state, hot keys, fan-out — and rank what breaks first. Not new design.
---

# scalability-review

> Every system has a first thing that breaks at 10× load. Find it before traffic does — by looking for serialization points, shared state, and amplification, not for slow code.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Before a launch, campaign, tenant onboarding, or a planned 3–10× growth step.
- After an incident where load exposed a limit and you want the *next* limit, not just this one.
- Reviewing a design doc or architecture diagram for scalability risk.

Not this when: you're creating the design from scratch — `polymath-scalability:system-design`; the issue is one slow endpoint's tail — `polymath-performance:backend-tail-latency`; or you need the date a known resource runs out — `polymath-sre:capacity-plan`.

## Inputs

- The architecture (diagram or description): tiers, datastores, queues, external dependencies, deployment topology.
- Current load and headroom per component (utilization, QPS, connections, queue depth) and the growth target.
- Known incidents and the data distribution (largest tenants, hottest keys).
- Measured per-component limits if any — mark untested limits `[VERIFY]`.

Without current measurements say so, and rank by structural risk only.

## Procedure

1. **Trace the request paths** (the top 2–3 by traffic and by business value). For each hop record sync/async, fan-out count, state touched, and the capacity limit if known.
2. **Apply the scalability lenses to every component and hop** — each is a source of "first to break":
   - **Single writer / serialization point**: one primary DB, one leader, a global lock, a single-threaded service, a sequence/counter row, a unique-id generator. Throughput is capped by one node regardless of fleet size (Amdahl; and the Universal Scalability Law adds coherence cost — adding nodes can *reduce* throughput when they contend).
   - **Shared mutable state**: sessions in memory, in-process caches that must agree, sticky routing, a shared cache or DB as a coordination point. Stateless tiers scale horizontally; stateful ones need partitioning or externalizing.
   - **Hot keys / skew**: one tenant, celebrity, item, or "latest" key absorbing a disproportionate share; check the top-N share of traffic and data. Even partitioning fails under skew.
   - **Amplification**: fan-out on write or read (one request → N downstream calls), N+1 queries, retries multiplying load, chatty microservice chains (latency and failure probability multiply per hop), thundering herds on cache expiry or reconnect.
   - **Unbounded things**: queues, in-memory buffers, result sets, partitions, connection counts, per-tenant data, metric/label cardinality. Unbounded growth is a future outage with a date.
   - **Connection and thread limits**: pool sizes × instance count vs the database's `max_connections`; thread-per-request vs async; file descriptors; ephemeral ports; per-IP/NAT limits.
   - **Coordination and consensus**: distributed locks, cross-shard transactions, 2PC, leader election, synchronous cross-region calls — latency and availability both degrade with scale.
   - **Batch vs online contention**: reports, backfills, migrations, or cron stampedes sharing resources with the user path.
   - **Dependency limits**: third-party rate limits and quotas, cloud service limits (API rate, IOPS, per-partition throughput), licensing caps, DNS/TLS handshake costs.
   - **Cost scaling**: components whose cost grows super-linearly with load (cross-AZ/region traffic, per-request pricing, logging volume).
3. **Quantify each suspect.** Current load vs its limit → headroom multiple (e.g. "primary writes at 38% of measured ceiling = 2.6× headroom"). Use `polymath-scalability:capacity-estimation` for projected load; unmeasured limits are `[VERIFY]` with the test that would measure them (`polymath-test-automation:load-test`).
4. **Rank by (headroom multiple, time-to-fix, blast radius)** — the lowest headroom with the longest fix time goes first. Identify *what breaks first and how* (graceful degradation vs cascading failure — `polymath-architecture:resilience-design`).
5. **For each top risk, give the lever and its cost**: scale out, partition, cache, async/queue, batch, shed load, redesign the data model, remove the hop. Prefer the cheapest lever that clears the target with margin; link the deeper skill (`polymath-database:db-scaling-strategy`, `partitioning-sharding`, `polymath-scalability:async-workload-design`).
6. **Define the verification**: load tests at the target multiple with realistic skew (not uniform keys), a failure-injection check (`polymath-sre:chaos-experiment`), and the alert/trigger that fires before the limit.

## Output

```text
Scalability review: checkout platform — target 5× (Black Friday)

Request path: edge → api-gw → checkout-svc → {inventory-svc (sync), pricing-svc (sync), payments (sync)} → orders-db (PG primary)

Rank  Risk                                   Evidence / headroom                         Breaks as                  Lever (cost)
1     orders-db single writer                writes 4.1k/s of ~9k measured ceiling = 2.2×; need 5× → short by 2.3×   latency cliff → timeouts → retry storm   archive + batch inserts (days); then partition/shard decision (weeks) — db-scaling-strategy
2     inventory-svc hot SKUs                 top-10 SKUs = 31% of reads [VERIFY: Black Friday mix]; row lock on stock decrement   lock queue on hot rows     split stock counter into N buckets / reserve via queue (days)
3     checkout → 3 sync hops                 combined availability 99.9%³ ≈ 99.7%; p99 sum = 1.9 s of 2 s budget   tail + cascading failure   parallelize pricing+inventory; timeout/fallback; shed at edge (days)
4     pool math                              40 pods × 20 conns = 800 vs max_connections 500   connection refusal on scale-out   pooler (hours)
5     batch export 02:00                     shares primary with prime-time order sync       IO contention              move to replica (hours)
Not a risk (checked): stateless tier (HPA verified at 4×); CDN; auth.
Verification: load test at 5× with Zipf SKU skew; kill one inventory pod and the pricing dependency; alert at orders-db write IOPS > 60% of ceiling.
Unknowns: [TBD: payments provider rate limit at 5×] — ask vendor + test in sandbox.
```

## Quality bar

- Risks are structural (serialization, skew, amplification, unbounded), each with measured or `[VERIFY]` headroom against the target multiple.
- Ranking says what breaks first and *how* (cliff vs degrade), not only that it is risky.
- Every top risk has a lever with a cost and a pointer to the deeper design skill.
- Tests use realistic skew; uniform-key load tests are flagged as insufficient.
- Components checked and cleared are listed, so a reviewer can argue with the elimination.

## Anti-patterns to avoid

- Reviewing code hot spots instead of architecture limits.
- "Add more instances" for a single-writer or shared-state bottleneck.
- Averaging: scale limits show up in the tail, in the hottest key, and in the biggest tenant.
- Testing at 5× with uniform data and declaring victory.
- Listing 12 equal "risks"; rank them, and name the first.
- Ignoring third-party and cloud-service quotas.
