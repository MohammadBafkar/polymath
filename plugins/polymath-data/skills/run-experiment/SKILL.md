---
name: run-experiment
description: Plan an A/B (or A/B/n) experiment — hypothesis, primary + guardrail metrics, MDE + sample size + duration, randomization, stop conditions.
---

# run-experiment

> Pin an experiment's design before launching. Output: a doc the on-call analyst can read in 90 seconds and the launch reviewer can approve without re-asking.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new feature is going behind an experiment (flag at 0/50/0 split).
- An existing experiment's plan has gaps (no MDE, no guardrail, no stop rule).
- Pre-`experimentToGA` workflow.

## Inputs

- Hypothesis (required) — testable, one variable, one direction.
- Primary metric (required) — what success looks like.
- Guardrail metrics (required) — what *can't* regress.
- Baseline values + traffic (required) — current metric mean + standard deviation (or the baseline rate for a proportion), daily eligible units. Missing: the sizing line reads `[TBD: …]` and the plan is not launch-ready — never invent a baseline.
- Acceptable MDE (optional) — the smallest effect worth detecting; absent, ask the owner (unattended: propose one, marked `[VERIFY: MDE]`).

## Procedure

1. **Hypothesis** — write it as: "Changing X will move primary-metric by ≥ MDE without regressing guardrails by > tolerance."
2. **Primary metric.** One metric. If you need two, you have two experiments. Make it:
   - Observable in your analytics within experiment duration.
   - Tied to the North Star (see `metrics-tree`).
   - Not the same as the variable under test (you'd be measuring tautology).
3. **Guardrails** — 2-3 max. Latency, error rate, key downstream conversions. State the regression tolerance per guardrail.
4. **MDE + sample size + duration — run the bundled script, never compute by hand.** Defaults: power 0.8, α = 0.05 two-sided; with more than two variants it applies Bonferroni (α / (k − 1) per comparison vs control):

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/run-experiment/scripts/sample-size.py" \
     --metric mean --sigma 2000 --mde 100 --daily-eligible 80000 --allocation 1.0
   # proportion: --metric proportion --baseline 0.12 --mde 0.01   (or --mde-relative 5)
   ```

   It uses the exact normal-approximation formulas (Lehr's `16σ²/MDE²` is the α = 0.05 / power 0.8 shortcut of the mean case), converts to days of traffic, rounds the run **up to whole weeks with a 7-day floor** (weekday vs weekend behavior), and marks the plan **UNDERPOWERED** past the 4-week cap — printing the MDE that is detectable in 28 days so the owner can pick a bigger MDE or a larger allocation. Paste its block verbatim.
   - These formulas assume the metric is a mean or proportion **per randomization unit**. Percentiles (p99 latency) and ratios with a different denominator (per-request metrics under user randomization) need the delta method or a bootstrap — and usually far more samples.
5. **Do not launch an UNDERPOWERED plan** without the owner explicitly accepting the longer run or the larger MDE in writing (in the plan file).
6. **Randomization unit.** User-level for product changes; session-level for content / UX experiments where multi-device matters; cluster-level (org / org-pair) for B2B to avoid contamination.
7. **Allocation.** 50/50 once tooling supports it; 90/10 (ramp) only when risk is high and you accept lower power. Document.
8. **Stop conditions.**
   - **Success** — at the planned sample size, the primary effect is statistically significant in the hypothesized direction and guardrails are clean. (The MDE sizes the test; the observed effect doesn't have to exceed it.)
   - **Failure** — primary regresses with confidence; or guardrail breach.
   - **Inconclusive** — at duration cap, primary effect is within noise.
   - **Emergency** — incident, ethics issue, regulatory; immediate halt independent of stats.
   - **No peeking:** don't stop early because a daily look shows significance — repeated looks inflate false positives. Analyze at the planned sample size, or pre-register a sequential method (group-sequential bounds, always-valid p-values) that allows early stopping.
   - **Sample-ratio mismatch:** before reading any metric, check the observed split against the plan — `python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/run-experiment/scripts/sample-size.py" --srm 50421,49579 --split 50,50`. p < 0.001 means the assignment is broken and the results are void.
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

Sample size + duration (sample-size.py, verbatim)
  Experiment sizing (two-sided, α = 0.05, power = 0.8, 2 variants)
  Metric:   mean, σ = 2,000, MDE = 100 (absolute)
  z:        z(1−α/2) = 1.960, z(power) = 0.842
  n per variant: 6,280   (total 12,560)
  Traffic:  80,000 eligible/day × 100% in experiment
  Duration: 0.16 days of traffic → run 7 days (whole weeks, 7-day floor)
  Verdict:  OK — within the 28-day cap
  SRM check: sample-size.py --srm <A>,<B> before reading any metric.

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
- MDE + sample size + duration all named, and every number came from the script.
- Stop conditions cover success / failure / inconclusive / emergency.
- Pre-registration with a frozen plan file before launch.

## Anti-patterns to avoid

- Picking the primary metric after the experiment ran. Inflates false positives.
- Multiple primary metrics. Statistical correction needed; usually skipped, results overstated.
- Duration < one week. Day-of-week confounds.
- Stopping the first day the dashboard shows p < 0.05.
- No guardrails. The single number that "won" was bought by a drop somewhere else.
