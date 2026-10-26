# Changelog — polymath-sre

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Added

- `slo-design/scripts/error-budget.py` — budget for any SLO and window, burn-rate alert table, and HEALTHY/ERODING/EXHAUSTED state from consumed minutes or requests (used by `slo-design` and `error-budget-policy`).
- `capacity-plan/scripts/headroom.py` — linear vs compound fit by R², ceiling-crossing date, event overlays, must-act-by date with an explicit `--as-of` (used by `capacity-plan` and `demand-forecast`).
- Unit tests for both.

### Changed

- Every skill declares its **Mode** — 6 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- Inputs for `slo-design`, `error-budget-policy`, `chaos-experiment`; exact shapes for `capacity-plan`, `demand-forecast`, `oncall-design`.

## [0.11.0]

### Fixed

- `slo-design` / `error-budget-policy`: 28-day budgets used 30-day figures (99.5% over 28d is 3h 21m 36s, not 3h 36m); burn-rate table gains short windows and both 30d/28d rates.
- `chaos-experiment`: `kubectl delete pod -l …` deleted every matching pod — the example now kills exactly one; the agent never runs an injection without explicit operator approval.
- `capacity-plan` / `demand-forecast`: boundaries no longer contradict each other (capacity-plan consumes the forecast).

## [0.8.0]

SRE craft: SLO design, error-budget policy, chaos experiments, capacity planning + demand forecasting, on-call program design.

### Skills

- **capacity-plan** — Plan forward capacity for a service or resource — current utilization, a growth model, headroom, scaling triggers, and cost; not short-term demand forecasting (demand-forecast).
- **chaos-experiment** — Design a chaos experiment — hypothesis, blast radius, abort criteria, observation, rollback; small-radius first.
- **demand-forecast** — Model capacity demand — growth (linear/compound/seasonal), translate to resource needs + headroom, and flag the lead time before a saturation breach.
- **error-budget-policy** — Author an error-budget policy — what happens when budget is healthy, eroding, or exhausted; named consequences not vibes.
- **oncall-design** — Design an on-call program — rotation + escalation, alert quality/actionability, runbook coverage, toil budget, handoff, and the operational-review loop.
- **slo-design** — Design an SLO — pick the right SLI per critical user journey, set the threshold by the 28-day error-budget arithmetic, document the measurement.
