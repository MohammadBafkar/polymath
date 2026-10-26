# Changelog — polymath-planning

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Added

- `estimate`: `scripts/pert.py` (per-step mean/σ, critical-path root-sum-square, 80% interval, P/O > 3 flags, draft markers).
- `forecast`: `scripts/monte-carlo.py` — seeded throughput Monte Carlo for "when" and "how many"; the method is chosen by a data rule, not preference.
- `prioritize`: `scripts/score.py` — RICE/WSJF with every input visible, a fixed tie-break, low-confidence flags, and ×0.5/×2 sensitivity on guessed inputs.
- Unit tests for all three.

### Fixed

- `estimate`'s worked example omitted the decompose flag on a step with P/O = 4; the example is now the script's real output.

### Changed

- Every skill declares its **Mode** — 4 analytical, 1 deterministic — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `work-breakdown`: Inputs; `write-plan`: unattended-run rule and the canonical slug rule.

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
