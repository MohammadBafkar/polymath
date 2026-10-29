# polymath-scalability

Scalable architecture and system-design craft for the Polymath marketplace — the staff/principal-level layer above the per-component skills.

## What it ships

- Skills:
  - `system-design` — end to end: requirements and SLOs → capacity → API/data model → components → scaling and failure modes → trade-offs and risks.
  - `capacity-estimation` — back-of-envelope QPS, bandwidth, storage, cache load, and node count, computed by a tested script (`scripts/estimate.py`); assumptions stated.
  - `scalability-review` — rank what breaks first in an existing architecture: single writers, shared state, hot keys, amplification, unbounded growth, quotas.
  - `async-workload-design` — queues vs streams vs workflow engines, idempotent workers, retries and DLQ, backpressure, priority lanes, autoscaling on queue age.
  - `rate-limiting-design` — limit keys, algorithms, distributed enforcement, 429 contract, fairness, observe-only rollout.
  - `multi-region-design` — active-active vs standby, RPO/RTO per data class, replication and conflicts, routing, failover and failback, residency.

Related skills elsewhere: `polymath-database:db-scaling-strategy`, `polymath-performance:high-load-io-design`, `polymath-architecture:resilience-design`, `polymath-sre:capacity-plan`.

## Installation

```bash
claude plugin install polymath-scalability@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
