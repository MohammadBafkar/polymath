---
name: rate-limiting-design
description: Design rate limits and quotas — token bucket vs window, limit keys, distributed enforcement, 429 headers, fairness, rollout.
---

# rate-limiting-design

> A rate limit protects a resource from a caller. Choose who is limited, by what, at which layer, and what the caller sees — then make the limiter cheaper and more available than the thing it protects.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Exposing a public or partner API, or protecting an internal service from noisy callers.
- Calling a rate-limited third party and needing to stay under its quota.
- Overload, scraping, credential stuffing, or one tenant degrading everyone else.

Not this when: the goal is shedding load by *system* health (concurrency/adaptive limits) rather than per-caller quotas — see `polymath-architecture:resilience-design`; or auth/abuse threat modeling — `polymath-security:stride-threat-model`.

## Inputs

- The protected resource and its measured capacity (QPS it sustains, cost per request, expensive endpoints).
- Caller identity available at the enforcement point (API key, user, tenant, IP, token), caller tiers/plans, and legitimate burst patterns.
- Where enforcement can happen (CDN/WAF, API gateway, service middleware, sidecar) and what shared store exists (Redis, gateway-native, local only).
- Business rules: free vs paid quotas, contractual limits, fairness expectations.

## Procedure

1. **Name the goal** — they need different designs: *fairness* (no tenant starves others), *protection* (stay under capacity), *abuse prevention* (brute force, scraping — also needs identity/behavior signals, not just rates), *cost control* (metered quota), or *client-side compliance* (outbound limits to a third party).
2. **Choose the limit key and tiers.** Prefer the strongest identity available (API key/tenant > user > IP; IP alone breaks behind NAT/mobile carriers and is bypassable). Often layer: a per-IP coarse limit at the edge, per-key limits at the gateway, per-tenant + per-endpoint cost limits in the service. Weight expensive operations (a search = 10 tokens, a read = 1) instead of one flat count.
3. **Choose the algorithm** for the behavior wanted:
   - **Token bucket** (rate + burst capacity): allows controlled bursts, the common default; refill rate = sustained limit, bucket size = tolerated burst.
   - **Leaky bucket / shaping**: smooths output to a constant rate (queue or delay) — for protecting a fixed-rate downstream.
   - **Fixed window counter**: simplest, but allows 2× burst at window boundaries.
   - **Sliding window log / counter**: precise or approximate smoothing at higher memory/CPU cost; the sliding-window counter is a good compromise.
   - **Concurrency limit** (in-flight cap): protects against slow requests that rate limits miss; combine with rates.
4. **Enforce at the right layer.** As early and cheaply as possible (edge/CDN/gateway) for volume and abuse; in-service for per-tenant cost fairness that needs business context. The limiter must not become a new single point: define fail-open vs fail-closed per endpoint (login/abuse → closed or degraded local limit; low-risk reads → open) and the behavior when the shared store is down.
5. **Distributed counting.** Options: central store (Redis with an atomic Lua script/`INCR`+`EXPIRE` or a token-bucket script — one round trip, atomic); local limiters with an even share of the global limit (`limit ÷ N` instances, fails under uneven routing); local + periodic sync (approximate, cheap); gateway-native. State the accuracy you accept (exact vs ±10–20%) and the added latency (≈ one cache RTT) against the budget. Use key TTLs so state is bounded; watch hot keys for a single abusive caller.
6. **Define the contract.** On limit: `429 Too Many Requests` with `Retry-After` (seconds or date) and, if you publish limits, `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset` (the IETF `RateLimit` header fields draft; document your exact semantics). Use a stable error body, a machine-readable code, and a docs link. Don't return 200 with an error, and don't silently drop. `503` is for server overload, `429` for caller quota.
7. **Make clients behave.** Document limits and burst; SDKs honor `Retry-After`, back off exponentially with jitter, and cap retries; idempotency keys for retried writes. Publish how to request a higher limit. For outbound calls to a third party, put a token bucket in front of the client sized *below* their limit and handle their 429s the same way.
8. **Set the numbers from capacity, not taste.** Sum of all granted sustained limits must stay under protected capacity, or you've issued oversold quotas — then decide on global load shedding by priority for the overage. Start from measured capacity × safety factor ÷ expected concurrent callers; give new/free tiers less. Roll out in **observe-only** mode first (count and log would-be rejections), then enforce, then tighten.
9. **Observe.** Rejections by key/tier/endpoint, near-limit callers, limiter latency and error rate, store health; alert on a sudden rise in 429s for a paying tenant (misconfiguration) and on limiter fail-open events. Provide a safe override (allow-list, temporary raise) with audit.
10. **Test it:** burst at the boundary, multi-instance accuracy, store outage behavior, clock skew, and a retry storm from clients that ignore `Retry-After`.

## Output

```text
Rate-limit design: public Orders API

Goal: fairness + protection (capacity 6k req/s sustained on the read path; writes 800/s).
Keys & tiers: API key (primary); per-IP 300/min at the CDN for unauthenticated routes; weights: GET=1, search=10, bulk export=50.
  free 60 req/min (1/s) burst 20 · pro 600/min (10/s) burst 100 · enterprise by contract
  Oversell check (all keys at sustained limit): free 1/s × 300 + pro 10/s × 400 + enterprise 1,200/s = 5.5k/s < 6k/s capacity [VERIFY: key counts, recompute monthly].
Algorithm: token bucket (rate = sustained, bucket = burst) + concurrency cap 25 in-flight per key.
Enforcement: gateway (edge) for per-key buckets via Redis Lua (atomic, 1 RTT ≈ 1 ms of the 15 ms budget); service-level cost limiter for exports.
Failure: Redis unreachable → fail open on GET with local per-instance cap (limit ÷ instances), fail closed on POST /auth/*.
Contract: 429 + Retry-After + RateLimit-Limit/Remaining/Reset; body {code:"rate_limited", retry_after:…, docs:…}; 503 reserved for load shedding.
Clients: SDK honors Retry-After, jittered backoff, max 3 retries; idempotency keys on POST.
Rollout: observe-only 2 weeks (log would-be 429s) → enforce for free → pro → enterprise; dashboards by key/tier.
Overrides: allow-list with expiry + audit; alert on 429 rate > 1% for a paying key.
Tests: boundary burst, 3-instance accuracy (±10%), Redis down, retry-storm client.
```

## Quality bar

- The goal (fairness / protection / abuse / cost) is stated, and the key, algorithm, and layer follow from it.
- Limits are derived from protected capacity with an oversell check, not picked from habit.
- The limiter's own failure mode (fail open/closed) and latency cost are specified per endpoint class.
- The 429 contract includes `Retry-After`, and client retry behavior is defined.
- Rollout begins in observe-only mode and includes an audited override path.

## Anti-patterns to avoid

- Limiting by IP alone (NAT, carriers, IPv6 rotation) and calling it abuse protection.
- Fixed-window counters at critical boundaries, or non-atomic `GET`-then-`SET` counters in a shared store.
- A limiter that fails closed for everything when its store is down — it becomes an outage.
- Granting quotas whose sum exceeds capacity.
- Returning `200` with an error body, or `429` without `Retry-After`.
- Enforcing for the first time directly in production with no observe-only pass.
