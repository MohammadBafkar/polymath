---
name: system-design
description: Design a scalable system end to end — SLOs, capacity, API and data model, components, scaling and failure modes, trade-offs.
---

# system-design

> A system design is a chain of justified trade-offs from requirements to numbers to components. Each box on the diagram exists because a number or a failure mode demanded it.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Designing a new service or major feature that must scale (feed, ingest pipeline, booking, notifications, search, payments).
- Preparing the architecture section of an RFC/design doc, or running a system-design review.
- A "will this scale?" question needs a structured answer rather than a list of technologies.

Not this when: you are reviewing an existing architecture for scale bottlenecks — `polymath-scalability:scalability-review`. For decomposing into services — `polymath-architecture:service-decomposition`; for the written decision — `polymath-writing:adr` / `rfc`.

## Inputs

- The problem and its users; functional scope (what's in, what's explicitly out).
- Non-functional targets: availability/latency SLOs (`polymath-sre:slo-design`), durability, consistency, security/compliance, cost ceiling, deadline.
- Scale: users/events and growth horizon — or let step 3 derive them and mark them assumptions.
- Constraints: existing platform, team size and skills, regulated data, vendor lock-in tolerance.

Missing requirement → state the assumption and the decision it drives; do not stall. In an unattended run, write the assumptions at the top and continue.

## Procedure

1. **Frame the problem.** One paragraph: who, what, why now. List functional requirements (3–7) and *non-goals*. Ambiguities become explicit assumptions.
2. **Set the non-functional targets as numbers**: availability (and what counts as down), p50/p99 latency per critical operation, durability (RPO), recovery (RTO), consistency (which reads may be stale, how stale), data residency. Vague adjectives ("fast", "highly available") don't count.
3. **Estimate capacity** with `polymath-scalability:capacity-estimation` — peak QPS, read/write split, bandwidth, storage over retention, fan-out. The dominant numbers pick the architecture; carry the uncertainty forward.
4. **Define the API and the data model.** The 3–6 core operations (sync/async, idempotency, pagination, versioning — `polymath-backend:api-design-rest`) and the entities, with their access patterns and the key each is looked up by. The access patterns, not the entities, choose the store (`polymath-database:db-scaling-strategy`, `nosql-partition-design`).
5. **Draw the simplest design that meets the numbers**, then add components only where a number or failure mode forces them. For each, name the problem it solves:
   - Stateless service tier behind a load balancer (scale out, health checks, graceful drain).
   - Datastore(s): engine and why; replication; partitioning and key.
   - Cache (what, where, invalidation — `polymath-performance:caching-tradeoffs`); CDN/edge for static and cacheable responses (`polymath-performance:http-edge-caching`).
   - Async work: queues/streams for anything not needed in the response (`polymath-scalability:async-workload-design`, `polymath-streaming:streaming-design`).
   - Search, analytics, and blob stores as separate read models fed by events/CDC, not queried from the OLTP store.
   - Rate limiting and admission control at the edge (`polymath-scalability:rate-limiting-design`).
6. **Walk the critical paths** (write path, read path, the one nasty path — fan-out, hot key, big tenant, retry) end to end with hop counts and the latency budget per hop (`polymath-performance:perf-budget`). Where it doesn't fit, redesign.
7. **Scaling plan.** For each tier: the scaling axis (horizontal, partition, replica), the bottleneck it will hit first, the trigger and the next step. Identify shared state, single writers, and hot keys now (`polymath-scalability:scalability-review` lenses).
8. **Failure and resilience.** For each dependency: timeout, retry (idempotent only), circuit breaker, bulkhead, fallback, load shedding (`polymath-architecture:resilience-design`); data durability and backup/restore; regional failure (`polymath-scalability:multi-region-design`); poison messages and replay. State what the user sees in each failure.
9. **Consistency and correctness.** Where there's a distributed write, say how it stays correct (outbox, saga, idempotency keys, unique constraints — `polymath-architecture:distributed-consistency`, `event-driven-design`).
10. **Security, observability, operations, cost.** AuthN/Z and data classification (`polymath-security:auth-design`), the SLIs/alerts that prove the SLOs (`polymath-observability:metrics-design`), deploy and rollback (`polymath-release:safe-rollout`), a rough unit cost per request/user and the main cost drivers.
11. **Record trade-offs and alternatives.** For each major decision: options considered, why this one, what it gives up, and the trigger that would reverse it. Link ADRs for the big ones.
12. **Call out risks and unknowns** with an owner and the experiment that retires each (load test, spike, vendor limits check).

## Output

```text
System design: notification service

Problem & scope
  Send transactional + marketing notifications (push/email/SMS) for 20 M users. Non-goals: in-app inbox, A/B content tooling.

Targets
  availability 99.9% (accepting a request); send latency p99 < 5 s for transactional; marketing within 15 min; at-least-once, no duplicates visible to user; RPO 0 for accepted requests, RTO 15 min.

Capacity (capacity-estimation)
  peak 40k notifications/s (campaign bursts) vs 2k/s steady; 40 GB/day logs; fan-out 1 → up to 3 channels.  Dominant uncertainty: burst size.

API / data
  POST /v1/notifications (Idempotency-Key) → 202 + id · GET /v1/notifications/{id}
  notification(id, user_id, template, status) keyed by id; per-user preferences keyed by user_id.

Design
  API → validate + dedupe → outbox → Kafka (topics by channel, partition key user_id) → channel workers → providers
  Priority: separate topics/consumer groups for transactional vs marketing (bulkhead; marketing can't starve OTP).
  Preferences: Postgres + cache (read-through, invalidate on write); status store: DynamoDB (id pk, TTL 30 d).
  Rate limiting: per-tenant at API; per-provider token bucket at workers (async-workload-design).

Critical paths
  transactional: API 15 ms → outbox commit → Kafka 10 ms → worker → provider (timeout 2 s, 1 retry w/ same key) → p99 ≈ 3 s.
  campaign: 40k/s burst absorbed by Kafka; marketing consumers scale to provider limits; lag SLO 15 min.

Failure modes
  provider down → circuit breaker, fail over to secondary provider, queue (bounded) otherwise DLQ + replay; Kafka down → API returns 503 (not lost: outbox retains); poison message → DLQ after 3 tries.

Trade-offs
  Kafka over SQS: replay + ordering per user, at cost of ops → ADR-12.  Single region now; multi-region trigger: SLO > 99.95% required.

Risks / unknowns
  [TBD: provider rate limits at campaign peak] → load test with sandbox providers (owner: notif team).
```

## Quality bar

- Every component traces to a requirement, a number, or a failure mode; nothing is there "because it's standard".
- Targets are numeric; capacity numbers come from `capacity-estimation` with assumptions marked.
- Critical paths include a latency budget and the failure behavior users see.
- Major decisions list the alternatives, what is given up, and the reversal trigger.
- Unknowns carry an owner and a retiring experiment rather than a confident guess.

## Anti-patterns to avoid

- Starting from a technology list (Kafka, Redis, microservices) instead of requirements and numbers.
- Designing for 100× the stated scale without a trigger, or ignoring a stated 10×.
- A diagram with no failure behavior, no data-ownership, or no scaling bottleneck named.
- Shared database between services as the integration mechanism.
- Dual writes (DB + broker) without an outbox.
- "Eventually consistent" with no statement of how stale or how users experience it.
