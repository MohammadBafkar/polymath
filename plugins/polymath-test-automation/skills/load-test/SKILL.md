---
name: load-test
description: Design a load/stress/soak test — k6/JMeter/Locust profile, realistic workload, ramp + think time, percentile thresholds. Generates load to find limits, not setting a budget (perf-budget).
---

# load-test

> Find where the system bends before users do. A load test that only proves the happy path at low concurrency proves nothing.

## When to use

- You need to know capacity, the breaking point, or whether a release holds under expected + peak traffic.
- The user asks for a load/stress/soak/spike test or a k6/Locust/JMeter script.
- A workflow invokes `polymath-test-automation:load-test`.

This *generates load to find limits*. It does not set the budget/SLO target (`polymath-performance:perf-budget`), diagnose a specific latency problem (`polymath-performance:backend-tail-latency`), or test correctness (`polymath-test-automation:e2e-flow`).

## Test types

- **Load** — expected peak; does it meet thresholds?
- **Stress** — ramp past peak to find the breaking point and failure mode.
- **Soak** — sustained load for hours to surface leaks/degradation.
- **Spike** — sudden surge; does it shed load gracefully and recover?

## Procedure

1. **Model the workload** — realistic mix of endpoints/journeys and their ratios, not one endpoint hammered. Use production traffic shape if available.
2. **Set ramp + think time** — virtual-user arrival rate, ramp-up, steady state, ramp-down; human think time between steps. Closed vs open model — state which.
3. **Define thresholds** — pass/fail on percentiles (p95/p99 latency, error rate, throughput); a load test with no thresholds is just a graph.
4. **Pick the type** (load/stress/soak/spike) for the question being asked.
5. **Author the script** (k6/Locust/JMeter) with parameterised data and environment, against a prod-like (not prod) target unless explicitly authorised.
6. **Report** — percentiles vs thresholds, the breaking point (for stress), saturation resource, and a pass/fail verdict.

## Quality bar

- The workload is a realistic mix with think time, not a single-endpoint flood.
- Thresholds are explicit (percentile + value); the run yields a pass/fail, not just charts.
- Test environment is prod-like and stated; running against prod requires explicit sign-off.
- Stress runs report the breaking point and the limiting resource, not just "it got slow".
