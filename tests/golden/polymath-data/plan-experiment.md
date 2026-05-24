---
plugin: polymath-data
scenario: plan-experiment
expect:
  invoked:
    - polymath-data:run-experiment
  output_matches:
    - "(primary metric|MDE|hypothesis)"
    - "(guardrail|tolerance)"
    - "(stop condition|sample size|duration)"
timeout_seconds: 60
---

# Prompt

> Plan an A/B test for refund-async-writes. Hypothesis: async writes
> drop refund p99 latency by 100ms without regressing completion rate.
> Baseline p99 = 1,200ms (σ=560ms). Daily eligible users = 80,000.

Use polymath-data:run-experiment.

# Acceptance

- One primary metric named, with MDE.
- ≤ 3 guardrails with regression tolerances.
- Sample size + duration derived (not asserted).
- Stop conditions cover success / failure / inconclusive.
- Pre-registration mentioned.
