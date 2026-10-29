---
name: resilience-design
description: Design resilience for a dependency call path — timeout, retry with backoff+jitter, circuit breaker, bulkhead, fallback, load-shedding — with a failure-mode table.
---

# resilience-design

> Every remote call fails eventually. Resilience is deciding what happens then — on purpose, with numbers — instead of discovering it during an incident.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A service calls a dependency (DB, API, queue) and you need the failure behavior specified, not implicit.
- Retries or timeouts already exist but caused a retry storm or cascading failure.
- A workflow invokes `polymath-architecture:resilience-design`.

Not this when: you are setting the latency/throughput target itself — that is `polymath-performance:perf-budget` / `backend-tail-latency`. This skill specifies behavior under failure, not the budget.
Per-caller quotas and 429 contracts are `polymath-scalability:rate-limiting-design`; queue backpressure and worker sizing are `polymath-scalability:async-workload-design`; regional failure is `polymath-scalability:multi-region-design`.

## Inputs

- The call path and the dependency's SLO/latency profile.
- Whether the call is on a user-blocking path or background.
- Idempotency of the operation (decides whether retry is even safe).

## Procedure

1. **Set a timeout** on every remote call — derived from the dependency's p99, not a round number, and within the caller's own deadline: propagate the remaining request deadline downstream so inner hops don't keep working after the caller gave up. No timeout is the root cause of most cascading outages.
2. **Decide retry**: only if the operation is idempotent or made so with an idempotency key. Use exponential backoff **with jitter**; cap attempts; retry at **one** layer only, under a retry budget (e.g. retries ≤ 10% of requests). Never retry permanent errors (most 4xx); `429`, `503`, and `408` are retryable — honor `Retry-After`.
3. **Add a circuit breaker** when a dependency can stay down: trip on an error-rate/latency threshold, go half-open to probe recovery. State the trip and reset conditions numerically.
4. **Isolate with bulkheads**: separate connection pools / thread pools per dependency so one slow dependency can't exhaust everything. Name the pool sizes.
5. **Define the fallback** for the open-circuit / timeout case: cached value, degraded response, queue-for-later, or a clean error. "Spin forever" is not a fallback.
6. **Shed load** at the edge under overload (reject early with 429 + Retry-After) rather than collapsing; protect with a concurrency limit.
7. **Avoid the anti-patterns**: retries layered at multiple tiers (multiplicative storm), retry without jitter (thundering herd), unbounded queues (hides the failure until OOM).
8. **Build the failure-mode table**: for each failure (timeout, 5xx, connection refused, slow), the chosen response and the user-visible effect.

## Output

```text
Resilience spec: checkout → payments-api (user-blocking, POST /charges)

Timeout:      1.2 s (payments p99 = 900 ms) within the 3 s request deadline; remaining deadline propagated
Retry:        2 attempts max, exponential backoff 100 ms × 2ⁿ with full jitter; only with Idempotency-Key;
              retry on 408/429/503 (honor Retry-After) and connect errors; never on other 4xx;
              retries only in the payments client (not the gateway); retry budget ≤ 10% of requests
Breaker:      open at ≥ 50% errors over 20 requests in 10 s; half-open after 30 s with 5 probes
Bulkhead:     payments pool 40 connections (of 200 total); separate from inventory's 20
Fallback:     breaker open → "payment temporarily unavailable, your cart is saved" (clean 503)
Load shed:    edge concurrency limit 500; above → 429 + Retry-After: 2

Failure mode          Response                          User sees
timeout               retry once with same key          slower checkout (≤ 2.5 s)
5xx                   retry, then breaker counts it     error after retries
connection refused    no retry after 2nd; breaker       fallback message
slow (p99 > 2 s)      timeout fires at 1.2 s            fallback message
```

Inline by default; when a workflow step or the user wants it kept, write it to `docs/architecture/<slug>-resilience.md` (slug from the system or context name, lowercased, non-`a-z0-9` runs → `-`).

## Quality bar

- Every remote call has an explicit, justified timeout.
- Retry is only enabled where the operation is idempotent, always with jitter and a cap.
- Each pattern's threshold is a number with a rationale, not "tune later".
- A fallback is named for every tripped/timed-out path.
