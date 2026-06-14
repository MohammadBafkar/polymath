# Changelog — polymath-architecture

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Architecture design craft: DDD context maps + aggregates, event-driven/integration design, resilience, service decomposition, distributed consistency.

### Skills

- **aggregate-design** — Design DDD tactical aggregates for a bounded context — aggregate roots, entities vs value objects, invariants, transaction/consistency boundaries, reference-by-id.
- **bounded-context-map** — Map a domain into DDD bounded contexts + a context map (customer-supplier, conformist, anti-corruption layer, shared kernel) with per-context ubiquitous language.
- **design-patterns-apply** — Review a design sketch against SOLID, GoF, and architectural patterns; flag anti-patterns at design time; not line-level code review (code-review).
- **distributed-consistency** — Choose a consistency model for a cross-node operation — strong/eventual/causal, CAP/PACELC trade-off, idempotency + dedup, and when consensus (Raft/quorum) is warranted vs simpler.
- **event-driven-design** — Design an event-driven flow — event catalog, choreography vs orchestration, saga + compensation, the outbox pattern for dual-writes, idempotent consumers, and CQRS read models.
- **integration-design** — Design integration between two services — sync vs async, API gateway / BFF placement, anti-corruption layer, contract + versioning, ports-and-adapters, and backpressure handling.
- **resilience-design** — Design resilience for a dependency call path — timeout, retry with backoff+jitter, circuit breaker, bulkhead, fallback, load-shedding — with a failure-mode table.
- **service-decomposition** — Map service boundaries in a monolith or split proposal — seam analysis by subdomain, a strangler-fig sequence, what stays, and a characterization-test plan.
