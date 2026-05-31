---
plugin: polymath-test-automation
scenario: load-test-search-api
expect:
  invoked:
    - polymath-test-automation:load-test
  output_matches:
    - "threshold"
    - "p95"
  not_invoked:
    - polymath-performance:perf-budget
    - polymath-test-automation:e2e-flow
timeout_seconds: 90
---

# Prompt

> We expect 2k req/s peak on the search API for a launch. Design a load
> test to see if we hold, and find where we break.

Use polymath-test-automation:load-test.

# Acceptance

- A realistic workload model with ramp + think time and a stated open/closed model.
- Pass/fail thresholds on percentiles (p95/p99, error rate); a stress phase reports the breaking point.
