---
plugin: polymath-performance
scenario: design-profile-cache
expect:
  invoked:
    - polymath-performance:design-cache-layer
  output_matches:
    - "(refund:profile|key.schema|version|v[0-9])"
    - "(TTL|jitter|EX)"
    - "(NX|lock|stampede)"
timeout_seconds: 60
---

# Prompt

> Design a Redis cache for GET /refund/profile/:id. The value takes 4 SQL
> queries to compute; reads are bursty and the same id is requested by
> multiple clients at once during peak.

Use polymath-performance:design-cache-layer.

# Acceptance

- Versioned key schema (e.g. v3 suffix).
- TTL with jitter.
- NX-lock stampede protection in the read path.
- Failure modes named (cache down, origin slow, hot key).
