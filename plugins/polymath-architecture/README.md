# polymath-architecture

Software-architecture design craft for the Polymath marketplace. Language- and
framework-agnostic design *techniques* — the modeling that turns requirements into
boundaries, contracts, and failure behavior.

This plugin owns the *techniques*; `polymath-writing` owns the resulting documents
(`adr`, `architecture-doc`, `rfc`), `polymath-decisions` owns trade-off scoring, and
caching lives in `polymath-performance`. These skills invoke those rather than restating them.

## What it ships

- Skills:
  - `bounded-context-map` — DDD strategic design: bounded contexts + a context map (customer-supplier, conformist, anti-corruption layer, shared kernel) with ubiquitous language.
  - `aggregate-design` — DDD tactical design: aggregate roots, entities vs value objects, invariants, transaction/consistency boundaries, reference-by-id.
  - `event-driven-design` — event catalog, choreography vs orchestration, saga + compensation, the transactional outbox, idempotent consumers, CQRS read models.
  - `resilience-design` — timeout, retry+backoff+jitter, circuit breaker, bulkhead, fallback, load-shedding, with a failure-mode table.
  - `service-decomposition` — seam analysis by subdomain, strangler-fig sequencing, keep-monolith judgment, characterization-test plan.
  - `distributed-consistency` — strong/eventual/causal model choice, CAP/PACELC, idempotency + dedup, consensus-vs-simpler.
  - `integration-design` — sync vs async, API gateway / BFF, anti-corruption layer, contract + versioning, ports-and-adapters, backpressure.
  - `design-patterns-apply` — design-time SOLID + GoF/architectural pattern selection and anti-pattern flags (distinct from line-level code review).

These compose into the `designSystem` workflow and stand alone when a single technique is needed.

## Installation

```bash
claude plugin install polymath-architecture@polymath
```

## Dependencies

- `polymath-core`
- `polymath-decisions`
- `polymath-writing`
- `polymath-thinking`

## License

MIT.
