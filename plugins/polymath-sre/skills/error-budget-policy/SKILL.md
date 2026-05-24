---
name: error-budget-policy
description: Author an error-budget policy — what happens when budget is healthy, eroding, or exhausted; named consequences not vibes.
---

# error-budget-policy

> Pin the actions tied to error-budget state. Output is a one-page policy a team can point to.

## When to use

- An SLO exists but the team doesn't know what to do when budget gets thin.
- Leadership wants reliability work to compete fairly with feature work.
- A workflow includes a release gate keyed to the error-budget state.

## Procedure

1. **Three states**:
   - **Healthy** — budget consumed < 50% of allowance for the window.
   - **Eroding** — 50–100% consumed.
   - **Exhausted** — over budget; service has missed its SLO.
2. **Per state, name the consequence**:
   - **Healthy**: feature work proceeds as usual.
   - **Eroding**: required reliability work in addition to features; no risky launches; new feature flags must be rollable.
   - **Exhausted**: feature freeze. The team works only on reliability and rollback hardening until budget is back to healthy. Exceptions require a named approver and a documented reason.
3. **Document the named approver** (a role, e.g. "VP Eng", not a person).
4. **Document the off-ramp** — how the team gets out of an exhausted state. Usually: SLO compliance for 14 consecutive days, or a budget reset following a major incident postmortem.
5. **SLO trust** — once a quarter, review whether the SLO threshold still matches user expectations. Don't move the threshold to fit the budget; either accept the work or renegotiate the threshold with stakeholders.

## Output

```text
Error-budget policy: refund-service (SLO: 99.5% / 28d)

State: HEALTHY (< 50% of 3h 36m budget used)
  - Feature work proceeds as planned.
  - Standard release cadence.

State: ERODING (50–100% of budget used)
  - Mandatory: every PR includes a reliability or test improvement.
  - No "risky" launches (defined: schema changes, dependency upgrades,
    new external integrations).
  - Feature flags required for new features; must be rollable < 1m.
  - Daily 5-min standup on burn-rate.

State: EXHAUSTED (> 100% of budget used)
  - Feature freeze. Reliability and rollback hardening only.
  - Exceptions require VP Eng sign-off; reason recorded.
  - Resume normal work after 14 consecutive days of compliant SLO.

Quarterly review:
  - Does the 99.5% threshold still match what users need?
  - Is the SLI definition still right (latency cutoff, success codes)?

Anti-pattern guard:
  We do not move the SLO threshold to "fit" the consumed budget.
  If the SLO is genuinely wrong, we renegotiate with stakeholders
  in writing, not via a config tweak.
```

## Anti-patterns to avoid

- "When budget is low, we'll be careful" — not a policy.
- Allowing exceptions without an approver or paper trail.
- Lowering the SLO threshold to keep budget healthy. That's not reliability work.
