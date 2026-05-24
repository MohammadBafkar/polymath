---
plugin: polymath-performance
scenario: perf-budget-checkout
expect:
  invoked:
    - polymath-performance:perf-budget
  output_matches:
    - "(P95|P99)"
    - "(network|compute|DB|database)"
    - "(headroom|tripwire|80%)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Set a perf budget for /checkout sees totals (P99 latency).

Use polymath-performance:perf-budget. CUJ: User loads /checkout after
adding items. Audience: median-mobile. We want P99 ≤ 1 second.

# Acceptance

- One CUJ named.
- One percentile chosen (P99) + threshold (1,000 ms).
- Components decomposed (network / handler / DB / external / render); sums to ≤ threshold with ≥ 20% headroom.
- Tripwire at 80% of threshold.
- Renegotiation gated through an ADR.
