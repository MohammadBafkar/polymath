---
name: flag-rollout-plan
description: Plan a feature-flag rollout — flag key, default rule, targeting rules, ramp stages with success/abort criteria, retirement date.
---

# flag-rollout-plan

> Pin a flag's lifecycle before shipping the code behind it. Output is a rollout plan that names every stage, the abort criteria, and the date the flag retires.

## When to use

- A new feature is going behind a flag for staged rollout.
- An existing flag is being expanded (10% → 100%).
- A workflow's pre-deploy step needs a flag plan.

## Procedure

1. **Flag key** — kebab-case, semver-free name that survives renames (`refund-async-writes`, not `feature-1`).
2. **Default rule** for unauthenticated / unknown segments. Almost always `false`.
3. **Targeting rules** — segments + percentages. Stage them:
   - **Internal** — `email ends with @yourcompany.com` → 100%. Catches bugs the team hits first.
   - **Beta cohort** — segment `beta-customers` → 100%. Catches power-user bugs.
   - **Canary** — random 1–5% of production. First broad signal.
   - **Ramp** — 10% → 25% → 50% → 100% with named abort criteria per step.
4. **Success criteria** per ramp step. SLO doesn't regress; error rate doesn't spike; conversion funnel doesn't dip. Tie to specific metrics, not "feels okay".
5. **Abort criteria** — name what triggers a rollback. "Burn rate > 6× on the affected SLO for 30 min."
6. **Retirement date** — the date the flag becomes constant `true` (default behavior) or `false` (kill) and the conditional code is removed. Open flags rot; **flag without a retirement date is a bug**.

## Output

```text
flag-rollout-plan: refund-async-writes

Key:         refund-async-writes
Project:     production
Default:     false

Targeting rules:
  1. @yourcompany.com employees                       → true  (internal dogfood)
  2. segment:beta-customers                           → true  (beta cohort)
  3. percentageRollout: 5%   (ramp stage 1)
  4. percentageRollout: 25%  (ramp stage 2)
  5. percentageRollout: 100% (final)

Success criteria per ramp step (advance only if all hold for 2h):
  - refund p99 latency within 10% of pre-flag baseline.
  - refund 5xx rate ≤ 0.2%.
  - refund conversion (cart → completed refund) ≥ 92%.

Abort criteria (any one triggers rollback):
  - SLO burn rate > 6× over 30 min.
  - refund 5xx rate > 1% for 5 min.
  - any sev1/sev2 incident with the flag in the timeline.

Retirement:
  Target removal: 2026-08-31 (90 days from initial launch).
  Owner of retirement: payments team.
  Pre-retirement: flag-state audit — confirm 100% rollout for ≥ 30 days.
```

## Quality bar

- Flag key names the capability, not a release.
- Retirement date present.
- Per-step success criteria are observable (metric name + threshold).
- Abort criteria specific (not "anything bad").

## Anti-patterns to avoid

- Open-ended flag with no retirement date. Old flags = future bug surface.
- Single "100%" ramp with no canary. Burns trust when it breaks.
- Success criteria like "looks fine in dashboards". Pin a metric.
- Letting the flag default to `true` for "convenience". Default-deny.
