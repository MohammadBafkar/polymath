# Changelog — polymath-scalability

<!-- markdownlint-disable MD024 -->

## [Unreleased]

New plugin: scalable architecture and system design.

### Skills

- **system-design** — Design a scalable system end to end — SLOs, capacity, API and data model, components, scaling and failure modes, trade-offs.
- **capacity-estimation** — Do back-of-envelope sizing — QPS, bandwidth, storage, cache load, node count — via a script. Not a growth forecast (capacity-plan).
- **scalability-review** — Review an architecture for scale bottlenecks — single writers, shared state, hot keys, fan-out — and rank what breaks first. Not new design.
- **async-workload-design** — Design async and background processing — queue vs stream, worker sizing, idempotency, retries and DLQ, backpressure, priority lanes.
- **rate-limiting-design** — Design rate limits and quotas — token bucket vs window, limit keys, distributed enforcement, 429 headers, fairness, rollout.
- **multi-region-design** — Design multi-region deployment — active-active vs standby, RPO/RTO, replication and conflicts, routing, failover. Not single-region HA.

### Tooling

- `capacity-estimation/scripts/estimate.py` — stdlib-only calculator with unit tests in `tests/`.
