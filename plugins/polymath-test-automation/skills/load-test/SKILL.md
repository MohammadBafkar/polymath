---
name: load-test
description: Design a load/stress/soak test — k6/JMeter/Locust profile, realistic workload, ramp + think time, percentile thresholds. Generates load to find limits, not setting a budget (perf-budget).
---

# load-test

> Find where the system bends before users do. A load test that only proves the happy path at low concurrency proves nothing.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- You need to know capacity, the breaking point, or whether a release holds under expected + peak traffic.
- The user asks for a load/stress/soak/spike test or a k6/Locust/JMeter script.
- A workflow invokes `polymath-test-automation:load-test`.

This *generates load to find limits*. It does not set the budget/SLO target (`polymath-performance:perf-budget`), diagnose a specific latency problem (`polymath-performance:backend-tail-latency`), or test correctness (`polymath-test-automation:e2e-flow`).

## Inputs

- The question (required): does it hold expected peak, where does it break, does it leak over hours, does it survive a surge?
- The target environment (required) — prod-like, never prod without explicit sign-off from the service owner. Generating load is a side effect: show the exact command and target, and run it only on the operator's go-ahead.
- Traffic shape (optional): production mix, peak RPS, think times. Absent: derive from access logs or analytics if readable; otherwise propose a mix marked `[VERIFY: traffic mix]`.
- Thresholds (optional): from `polymath-performance:perf-budget` or the SLO. Absent: propose them, marked `[VERIFY]`.

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
6. **Report** — percentiles vs thresholds, the breaking point (for stress), saturation resource, and a pass/fail verdict. **Results come only from an actual run's output.** Without a run, deliver the script and plan with the verdict `NOT RUN` — never estimated numbers.

## Output

`loadtest/<slug>.js` (or `.py` / `.jmx`) plus a report in this shape:

```text
Load test: refund API — stress            tool: k6 (open model, arrival-rate)

Target:     staging-eu (prod-like: same instance types, 1/4 node count) — approved by @payments-oncall
Workload:   60% GET /refunds/{id} · 30% POST /refunds · 10% GET /orders/{id}/refunds; think time 1–3s
Profile:    ramp 0→400 RPS over 10m, hold 10m, step +100 RPS every 5m until thresholds fail
Thresholds: p95 < 300 ms · p99 < 800 ms · errors < 0.5%

Result (k6 summary, run 2026-10-26 14:02 UTC):
  at 400 RPS  p95 182 ms  p99 410 ms  errors 0.02%   PASS
  at 700 RPS  p95 290 ms  p99 790 ms  errors 0.10%   PASS
  at 800 RPS  p95 610 ms  p99 2.1 s   errors 3.40%   FAIL ← breaking point
Saturation: Postgres connection pool (100/100 in use from 760 RPS)
Verdict:    holds expected peak (400 RPS) with 1.9× headroom; breaks at ~800 RPS on DB connections
```

## Quality bar

- The workload is a realistic mix with think time, not a single-endpoint flood.
- Thresholds are explicit (percentile + value); the run yields a pass/fail, not just charts.
- Test environment is prod-like and stated; running against prod requires explicit sign-off.
- Stress runs report the breaking point and the limiting resource, not just "it got slow".
