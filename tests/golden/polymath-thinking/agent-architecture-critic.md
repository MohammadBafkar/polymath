---
plugin: polymath-thinking
scenario: agent-architecture-critic
agent: architecture-critic
expect:
  invoked:
    - architecture-critic
  output_matches:
    - "(fail-open|fail closed|partition|outage)"
    - "(alternative|gateway|token bucket)"
    - "(?i)(fatal|patchable|assumption)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Use the polymath-thinking architecture-critic agent.

Review this ADR draft:

Decision: Use Redis as the only backing store for /login rate-limit counters.
Redis is already available in production and is fast enough. If Redis is down,
the login service should continue operating normally. Keys are
`rate-limit:{ip}:{accountId}` and expire after 24 hours.

# Acceptance

- The agent challenges the Redis-only assumption.
- The output names the Redis outage policy risk.
- The output mentions the keying/privacy issue.
- The output proposes at least one alternative such as gateway-native limiting
  or a local token bucket fallback.
