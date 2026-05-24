# polymath-infra-redis

Redis craft for the Polymath marketplace.

## What it ships

- Skills:
  - `design-cache-layer` — key schema with version suffix, TTL with jitter, stampede protection via NX-lock, hot-key / big-key avoidance.
  - `audit-redis-config` — maxmemory policy, persistence (RDB/AOF), replication, slow log, ACL, TLS.
- Commands: `/polymath-infra-redis:design-cache`, `/polymath-infra-redis:audit-config`.

## Installation

```bash
claude plugin install polymath-infra-redis@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
