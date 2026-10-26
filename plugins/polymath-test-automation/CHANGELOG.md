# Changelog — polymath-test-automation

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 2 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `e2e-flow`: exact output; a spec that never ran is reported `NOT RUN`.
- `load-test`: Inputs (approved target, generating load is a side effect) and exact report; results come only from a real run.

## [0.8.0]

Test automation: browser end-to-end flows and load/stress/soak profiles, gated in CI.

### Skills

- **e2e-flow** — Author a browser end-to-end (e2e) test for a critical user journey — stable selectors, web-first waits, deterministic data. Full-stack UI flows, not unit tests or service contracts.
- **load-test** — Design a load/stress/soak test — k6/JMeter/Locust profile, realistic workload, ramp + think time, percentile thresholds. Generates load to find limits, not setting a budget (perf-budget).
