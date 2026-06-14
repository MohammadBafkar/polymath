# Changelog — polymath-performance

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Performance craft: budget setting, backend tail-latency investigation, caching tradeoffs.

### Skills

- **audit-redis-config** — Audit a live Redis instance's config — maxmemory + eviction, persistence (RDB/AOF), replication, slow-log, ACL, TLS. Audits existing settings; not cache design (design-cache-layer).
- **backend-tail-latency** — Investigate backend P99/P999 tail latency — coordinated GC, lock contention, queue depth, slow downstream, retry storms; surface ONE dominant cause.
- **caching-tradeoffs** — Design a cache — what's cached, where (local / regional / shared), invalidation strategy, staleness tolerance, named failure modes (stampede, poisoning, drift). Strategy, not Redis key/TTL design.
- **design-cache-layer** — Design a Redis cache layer — key schema, TTLs, eviction policy, stampede + thundering-herd protection, hot-key + big-key avoidance. Use after caching-tradeoffs picks where; not Redis server config.
- **perf-budget** — Set a perf budget — per critical user journey, single percentile + threshold, explicit budget components (network / compute / dependencies), tripwire alerts. Backend journeys; not web CWV or mobile.

### Commands

- **/audit-redis-config** — Audit a live Redis instance's settings; command entry point for the audit-redis-config skill.
- **/design-cache** — Design a Redis cache layer — key schema, TTL strategy, stampede protection, eviction.
