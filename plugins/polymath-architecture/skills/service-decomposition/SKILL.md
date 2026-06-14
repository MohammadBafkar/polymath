---
name: service-decomposition
description: Map service boundaries in a monolith or split proposal — seam analysis by subdomain, a strangler-fig sequence, what stays, and a characterization-test plan.
---

# service-decomposition

> Most microservice pain is a boundary drawn for the org chart, not the domain. Decompose by subdomain and data ownership, extract one seam at a time, and keep what works.

## When to use

- A monolith is hard to change/scale and a split is being considered.
- A "let's do microservices" proposal needs a boundary critique before anyone writes a service.
- A workflow invokes `polymath-architecture:service-decomposition`.

Not this when: you are defining the domain language/contexts from scratch — do `bounded-context-map` first; this skill turns contexts into a *technical* extraction plan. For the cutover/rollback mechanics of a live migration, that is the migration playbook.

## Inputs

- The current monolith's modules, the painful change/scale points, and the data model.
- A bounded-context map if one exists.

## Procedure

1. **Decide if you should split at all.** Default to a *modular monolith* unless there is a concrete forcing function: independent scaling, independent deploy cadence, team autonomy at scale, or fault isolation. Premature splitting buys distributed-systems cost for no benefit — say so when that is the case.
2. **Find seams** along subdomain boundaries and data ownership: a candidate service owns its data and exposes it only via API. A boundary that requires a shared/joined database is not a boundary.
3. **Rank candidates** by *value ÷ risk*: high-churn or independently-scaling modules with clean data ownership extract first; tangled core modules last.
4. **Plan a strangler-fig sequence**: route a slice of traffic/functionality through the new service behind a facade while the monolith still runs; migrate incrementally; never a big-bang rewrite.
5. **Handle the data**: split the schema, choose the migration (dual-write + backfill, or change-data-capture), and define how cross-service queries that used to be JOINs now work (API composition or a read model).
6. **Protect behavior with characterization tests**: capture the monolith's current observable behavior as tests *before* extracting, so the extraction is verifiably behavior-preserving.
7. **Account for the new costs**: network failure, eventual consistency, distributed tracing, deployment surface. If the list is long and the benefit thin, recommend staying modular-monolith.

## Output

- A one-page plan: keep-monolith vs split recommendation, ranked extraction candidates (value/risk + data-ownership note), the strangler-fig sequence, the data-split approach, and the characterization-test plan.

## Quality bar

- "Stay a modular monolith" is on the table and chosen when the forcing function is absent.
- Each candidate service owns its data — no shared-database boundaries.
- Extraction is incremental (strangler-fig) and guarded by characterization tests.
- The added distributed-systems cost is named, not hand-waved.
