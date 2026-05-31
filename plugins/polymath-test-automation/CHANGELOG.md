# Changelog — polymath-test-automation

## [Unreleased]

### Added

- `e2e-flow` skill — author a browser end-to-end test for a critical user
  journey: role/text selectors, web-first (state-based) waits, deterministic
  per-test data, one journey per spec, trace on failure.
- `load-test` skill — design a load/stress/soak/spike test with a realistic
  workload model, ramp + think time, and explicit pass/fail thresholds on
  percentiles (k6/JMeter/Locust).
- Golden fixtures and skill-triggering tests for both.
