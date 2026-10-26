# Changelog — polymath-planning

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `estimate`: summing every optimistic and pessimistic value is not a 90% interval — uses σ ≈ (P−O)/2.56 per step, root-sum-square aggregation, an 80% interval, and a correlation caveat.

## [0.8.0]

Planning craft: write-plan, work-breakdown, three-point estimate.

### Skills

- **estimate** — Estimate a work breakdown with a lightweight three-point method (optimistic, expected, pessimistic); surfaces uncertainty rather than a single date.
- **forecast** — Model a delivery date/scope as a probability range — reference-class, throughput/Monte-Carlo, cone of uncertainty; range forecasting from data, not per-item estimation (estimate).
- **prioritize** — Prioritize a backlog or feature set — RICE, WSJF/cost-of-delay, MoSCoW, Kano, value-vs-effort 2x2, Now/Next/Later; exposes value/effort/confidence inputs, never an opaque score.
- **work-breakdown** — Decompose a goal or plan into independently completable steps; each step produces an observable artifact. Engineering task WBS; not story slicing (decompose-epic) or the plan doc (write-plan).
- **write-plan** — Write a project / change plan to docs/plans/<slug>.md from the canonical Plan template; What, Why, Approach, Work breakdown, Risks, Verification, Out of scope. The full plan doc, not a standalone WBS.
