# polymath-test-automation

Test-automation craft beyond the unit level: protect the critical journeys with browser end-to-end tests, and find the system's limits with load/stress/soak tests.

## What it ships

- Skills:
  - `e2e-flow` — author a browser end-to-end test for a critical user journey (Playwright-style role/text selectors, web-first waits, deterministic data, one journey per spec).
  - `load-test` — design a load/stress/soak/spike test (k6/JMeter/Locust) with a realistic workload model, ramp + think time, and pass/fail thresholds on percentiles.

## Why it exists

The audit found `polymath-qa` covered unit/coverage/strategy but had no browser e2e or load/stress authoring — a structurally absent phase. This plugin adds the distinct e2e and load toolchains, sitting between `polymath-qa:test-strategy` (the plan) and `polymath-devops:ci-pipeline-github` (where these gate).

## Installation

```bash
claude plugin install polymath-test-automation@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
