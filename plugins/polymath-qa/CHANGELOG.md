# Changelog — polymath-qa

## [Unreleased]

### Added

- `test-smell` skill — detect test smells/anti-patterns (over-mocking, fragile
  assertions, slow setup, flaky timing) in an existing suite, each flagged with
  its layer and a refactor.
- `integration-contract` skill — design integration and consumer-driven contract
  tests for a service boundary (stub-vs-hit, fixtures, failure modes).
- `assertion-quality` skill — strengthen assertions to test behavior not
  implementation, with one clear reason-to-fail per test.
- Skill-triggering tests for all three.

## [0.1.0]

### Added

- Initial v0.1 components: `test-strategy`, `coverage-gap`, `unit-tests` skills.
