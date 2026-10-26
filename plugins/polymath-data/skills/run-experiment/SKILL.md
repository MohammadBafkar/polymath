---
name: run-experiment
description: Plan an A/B (or A/B/n) experiment — hypothesis, primary + guardrail metrics, MDE + sample size + duration, randomization, stop conditions.
---

# run-experiment

> Pin an experiment's design before launching. Output: a doc the on-call analyst can read in 90 seconds and the launch reviewer can approve without re-asking.

## When to use

- A new feature is going behind an experiment (flag at 0/50/0 split).
- An existing experiment's plan has gaps (no MDE, no guardrail, no stop rule).
- Pre-`experimentToGA` workflow.

## Inputs

- Hypothesis (required) — testable, one variable, one direction.
- Primary metric (required) — what success looks like.
- Guardrail metrics (required) — what *can't* regress.
- Baseline values + traffic (required) — current metric mean + variance, daily eligible users.
- Acceptable MDE (optional) — minimum detectable effect; derive sample size if missing.

## Procedure

1. **Hypothesis** — write it as: "Changing X will move primary-metric by ≥ MDE without regressing guardrails by > tolerance."
2. **Primary metric.** One metric. If you need two, you have two experiments. Make it:
   - Observable in your analytics within experiment duration.
   - Tied to the North Star (see `metrics-tree`).
   - Not the same as the variable under test (you'd be measuring tautology).
3. **Guardrails** — 2-3 max. Latency, error rate, key downstream conversions. State the regression tolerance per guardrail.
4. **MDE + sample size.**
   - Statistical power 0.8, significance α = 0.05 are the usual defaults.
   - Sample size per variant (two variants, α = 0.05 two-sided, power 0.8 — Lehr's rule): `n ≈ 16 × σ²/MDE²` for a difference in means; `n ≈ 16 × p(1−p)/MDE²` for a proportion with an absolute MDE.
   - At known daily traffic, the duration falls out: `days = (variants × n) / (daily_eligible × fraction_of_traffic_in_experiment)`.
   - These formulas assume the metric is a mean or proportion **per randomization unit**. Percentiles (p99 latency) and ratios with a different denominator (per-request metrics under user randomization) need the delta method or a bootstrap — and usually far more samples.
5. **Duration floor + cap.**
   - Floor: at least one full weekly cycle (weekday vs weekend behavior).
   - Cap: 4 weeks max; if MDE requires longer, the experiment is under-powered for your traffic — pick a bigger MDE or larger allocation.
6. **Randomization unit.** User-level for product changes; session-level for content / UX experiments where multi-device matters; cluster-level (org / org-pair) for B2B to avoid contamination.
7. **Allocation.** 50/50 once tooling supports it; 90/10 (ramp) only when risk is high and you accept lower power. Document.
8. **Stop conditions.**
   - **Success** — at the planned sample size, the primary effect is statistically significant in the hypothesized direction and guardrails are clean. (The MDE sizes the test; the observed effect doesn't have to exceed it.)
   - **Failure** — primary regresses with confidence; or guardrail breach.
   - **Inconclusive** — at duration cap, primary effect is within noise.
   - **Emergency** — incident, ethics issue, regulatory; immediate halt independent of stats.
   - **No peeking:** don't stop early because a daily look shows significance — repeated looks inflate false positives. Analyze at the planned sample size, or pre-register a sequential method (group-sequential bounds, always-valid p-values) that allows early stopping.
   - **Sample-ratio mismatch:** check the observed split against the planned allocation (chi-square) before reading any metric; an SRM means the assignment is broken and the results are void.
9. **Pre-registration.** Write the plan before launch and freeze. Post-hoc metric switching ("oh, let's check this other one") inflates false-positive rate.

## Output

```text
run-experiment: refund-async-writes

Hypothesis
  Changing the refund pipeline to async writes will reduce refund p99
  latency by ≥ 100ms without regressing refund-completion-rate by > 0.3%.

Variants
  A (control)   — current sync write path
  B (treatment) — async write to refund-worker

Allocation
  50/50, user-level randomization.

Primary metric
  mean refund latency per user, ms (lower-is-better). Baseline 1,200 ms;
  σ = 2,000 ms (heavy tail); MDE 100 ms.
  (p99 latency is tracked as a guardrail, analyzed by bootstrap.)

Guardrails
  refund_completion_rate              tolerance: > -0.3 percentage points
  refund_5xx_rate                     tolerance: < +0.2 percentage points

Sample size + duration
  daily eligible users: 80,000; 100% of traffic in the experiment
  n per variant ≈ 16 × 2,000² / 100² = 6,400
  → days ≈ (2 × 6,400) / (80,000 × 1.0) = 0.16 → floor: 1 weekly cycle = 7 days.
  SRM check: chi-square on assignment counts before analysis.

Stop conditions (evaluated once, at day 7 — no early stop on significance)
  Success:     treatment mean lower than control, p < 0.05, guardrails clean.
  Failure:     significant regression on primary OR any guardrail breach.
  Inconclusive: not significant at day 7.
  Emergency:   incident or guardrail breach → halt immediately.

Pre-registration
  Frozen 2026-05-23. Plan file: docs/experiments/refund-async-writes.md
```

## Quality bar

- One primary, ≤ 3 guardrails — never "we'll look at everything".
- MDE + sample size + duration all named.
- Stop conditions cover success / failure / inconclusive / emergency.
- Pre-registration with a frozen plan file before launch.

## Anti-patterns to avoid

- Picking the primary metric after the experiment ran. Inflates false positives.
- Multiple primary metrics. Statistical correction needed; usually skipped, results overstated.
- Duration < one week. Day-of-week confounds.
- Stopping the first day the dashboard shows p < 0.05.
- No guardrails. The single number that "won" was bought by a drop somewhere else.
