# Changelog — polymath-sre

<!-- markdownlint-disable MD024 -->

## [0.8.0]

SRE craft: SLO design, error-budget policy, chaos experiments, capacity planning + demand forecasting, on-call program design.

### Skills

- **capacity-plan** — Plan forward capacity for a service or resource — current utilization, a growth model, headroom, scaling triggers, and cost; not short-term demand forecasting (demand-forecast).
- **chaos-experiment** — Design a chaos experiment — hypothesis, blast radius, abort criteria, observation, rollback; small-radius first.
- **demand-forecast** — Model capacity demand — growth (linear/compound/seasonal), translate to resource needs + headroom, and flag the lead time before a saturation breach.
- **error-budget-policy** — Author an error-budget policy — what happens when budget is healthy, eroding, or exhausted; named consequences not vibes.
- **oncall-design** — Design an on-call program — rotation + escalation, alert quality/actionability, runbook coverage, toil budget, handoff, and the operational-review loop.
- **slo-design** — Design an SLO — pick the right SLI per critical user journey, set the threshold by the 28-day error-budget arithmetic, document the measurement.
