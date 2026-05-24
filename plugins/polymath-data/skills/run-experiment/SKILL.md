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
   - Sample size per variant: `n ≈ 16 × (σ/MDE)²` for a means test (Cohen's rule of thumb); `n ≈ 16 × p(1-p)/MDE²` for proportions.
   - At known daily traffic, the duration falls out: `days = (2 × n) / daily_eligible × allocation_fraction`.
5. **Duration floor + cap.**
   - Floor: at least one full weekly cycle (weekday vs weekend behavior).
   - Cap: 4 weeks max; if MDE requires longer, the experiment is under-powered for your traffic — pick a bigger MDE or larger allocation.
6. **Randomization unit.** User-level for product changes; session-level for content / UX experiments where multi-device matters; cluster-level (org / org-pair) for B2B to avoid contamination.
7. **Allocation.** 50/50 once tooling supports it; 90/10 (ramp) only when risk is high and you accept lower power. Document.
8. **Stop conditions.**
   - **Success** — primary metric crosses MDE with statistical significance, guardrails clean.
   - **Failure** — primary regresses with confidence; or guardrail breach.
   - **Inconclusive** — at duration cap, primary effect is within noise.
   - **Emergency** — incident, ethics issue, regulatory; immediate halt independent of stats.
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
  refund_p99_latency_ms (lower-is-better). Baseline 1,200ms; MDE 100ms.

Guardrails
  refund_completion_rate              tolerance: > -0.3 percentage points
  refund_5xx_rate                     tolerance: < +0.2 percentage points

Sample size + duration
  daily eligible users: 80,000
  n per variant ≈ 14,000 (Cohen rule, σ=560ms, MDE=100ms)
  → days ≈ 14k × 2 / 80k = 0.35 → round up to 1 weekly cycle: 7 days.

Stop conditions
  Success:     primary < baseline by ≥ 100ms (p < 0.05), guardrails clean.
  Failure:     primary > baseline OR any guardrail breach.
  Inconclusive: 7 days elapsed, effect within ±50ms of baseline.

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
- No guardrails. The single number that "won" was bought by a drop somewhere else.
