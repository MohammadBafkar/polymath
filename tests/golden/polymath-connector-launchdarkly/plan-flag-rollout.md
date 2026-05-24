---
plugin: polymath-connector-launchdarkly
scenario: plan-flag-rollout
expect:
  invoked:
    - polymath-connector-launchdarkly:flag-rollout-plan
  output_matches:
    - "(refund-async-writes|kebab-case)"
    - "(retire|retirement)"
    - "(abort|rollback)"
timeout_seconds: 90
---

# Prompt

> Plan a rollout for a new feature flag that controls async writes in the refund pipeline.

Use polymath-connector-launchdarkly:flag-rollout-plan. The feature
is risky because async writes change ordering guarantees; we want
internal dogfood, then beta cohort, then a 5% canary, then a 25/100
ramp. SLO target: refund p99 latency within 10% of baseline.

# Acceptance

- Flag key is kebab-case and names the capability, not a release.
- Plan names internal → beta → canary → ramp stages explicitly.
- Success criteria pin to specific metrics with thresholds (not "looks fine").
- Abort criteria pin to specific signals (SLO burn-rate, error rate, sev1/sev2).
- Retirement date is present (open-ended flags are an anti-pattern).
