---
name: design-cache-layer
description: Design a Redis cache layer — key schema, TTLs, eviction policy, stampede + thundering-herd protection, hot-key + big-key avoidance. Use after caching-tradeoffs picks where; not Redis server config.
---

# design-cache-layer

> Cache design that survives Black Friday, not just the demo. Output: key schema, TTL strategy, write/read path, failure modes considered.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A read-heavy endpoint needs caching.
- An existing cache is causing incidents (stampedes, hot keys, memory pressure).
- A PRD says "use Redis" with no further detail.

## Inputs

- The cache shape decided by `polymath-performance:caching-tradeoffs` (what, where, invalidation, staleness) — required; without it, run that first.
- Traffic: request rate, key cardinality, value sizes, hot-key candidates (measured or `[TBD]`).
- The Redis deployment (optional): managed vs self-hosted, cluster vs single primary, memory limit.

## Related skills

- [`polymath-performance:caching-tradeoffs`](../caching-tradeoffs/SKILL.md)
  — vendor-agnostic decision: *what* to cache, *where* to cache,
  staleness tolerance, failure modes. Run that first to decide the
  shape; use this skill to ship the Redis layer.
- [`polymath-performance:audit-redis-config`](../audit-redis-config/SKILL.md)
  — once the cache layer is running, review `maxmemory`, eviction,
  persistence, replication.

## Procedure

1. **Identify the value.** Caching is for *expensive-to-compute, frequently-read, eventually-consistent* values. If the data is cheap to compute or strongly consistent, do not cache.
2. **Key schema.** Structured + versioned:
   ```
   <domain>:<entity>:<id>:v<version>      e.g. refund:profile:42:v3
   <domain>:list:<filter-hash>:v<version> e.g. refund:list:sha8af2:v3
   ```
   The `v<n>` suffix lets a deploy invalidate everything by bumping it; the alternative (deleting keys) is slow on large keyspaces.
3. **TTL strategy.**
   - Per-entry TTL with jitter: `TTL = base ± random(0, base/10)`. Prevents synchronized expiry storms.
   - Sliding TTL only when reads are bursty around a record (re-set on hit).
   - Negative caching: also cache "not found" for a shorter TTL to absorb 404 floods.
4. **Eviction.** `maxmemory-policy = allkeys-lru` for pure caches; `volatile-lru` if you also store non-cache data with no TTL.
5. **Read path with stampede protection.**
   ```
   value = GET key
   if value:
       return value
   # cache miss
   token = random_uuid()
   if SET nx:lock:key token NX EX=5:
       try:
           value = expensive_compute()
           SET key value EX=jittered_ttl
           return value
       finally:
           # release only OUR lock — compare-and-delete in one Lua call
           EVAL "if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) end return 0" 1 nx:lock:key token
   for attempt in 1..3:                      # someone else is computing
       sleep(50ms × attempt)
       value = GET key
       if value: return value
   return serve_stale_or_compute_without_caching()   # bounded wait, never spin forever
   ```
   Single-flight by lock; concurrent misses don't all hammer the origin. A plain `DEL` would delete another worker's lock if compute outlived the 5 s expiry.
6. **Write path.** Update-then-invalidate (`SET origin = new; DEL key`) is simpler than write-through. Know its race: a reader that fetched the old value before the write can re-populate the cache after the `DEL`. Bound it with the TTL, a version in the key/value, or a delayed second `DEL`, depending on how much staleness the data tolerates.
7. **Hot keys.** A key with > 1% of total RPS is a hot key. Strategies:
   - Shard the value into multiple keys (`refund:profile:42:shard:{0..9}` round-robin).
   - Use a local in-process cache in front (Caffeine / lru-cache) for sub-second TTL.
8. **Big keys.** A single key > 100KB or a single LIST/HASH with > 10k items is a big key. Cluster mode bites on slot rebalances; split.
9. **Failure modes.**
   - Cache down → origin slammed. Add a circuit breaker that fails open (skip cache) for a short window.
   - Origin slow + cache miss → request hangs. Set a *cache-fill timeout* and serve stale.
10. **Observability.** Hit ratio, miss latency, eviction rate, slow-log entries. Without these, you don't know if the cache is helping or hurting.

## Output

```text
design-cache-layer

Endpoint:   GET /refund/profile/:id
Value:      RefundProfile (~5KB JSON, computed from 4 SQL queries)

Key schema
  refund:profile:<id>:v3                                   primary
  nx:lock:refund:profile:<id>:v3   EX=5s, NX               stampede guard

TTL:        300s ± 30s (jitter)
Negative:   10s for not-found

Eviction:   allkeys-lru, maxmemory ~ 8GB.

Read path:
  GET → on miss, NX-lock → compute → SET EX=jittered → DEL lock.

Write path:
  Update SQL → DEL refund:profile:<id>:v3.

Failure modes covered:
  ✓ stampede via NX lock
  ✓ thundering herd via TTL jitter
  ✓ origin slowness via cache-fill timeout + stale-serve
  ⚠ hot key: monitor; shard if a single id exceeds 1% RPS

Observability: hit ratio, miss latency p99, eviction rate, slow-log.
```

## Quality bar

- Key schema versioned for cheap global invalidation.
- TTL has jitter.
- Stampede protection in the read path: token-owned lock, compare-and-delete release, bounded waiting.
- Failure modes named, not assumed.

## Anti-patterns to avoid

- TTL without jitter on a hot key. Synchronized expiry → origin stampede.
- Write-through caching for everything. Couples writes to cache latency.
- Forgetting negative caching. 404 floods are real.
- Using Redis as a primary store without persistence understanding. RDB + AOF have different durability stories.
