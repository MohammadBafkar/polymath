# Changelog — polymath-qa

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 6 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `assertion-quality`, `integration-contract`, `test-smell`: exact, ranked output shapes.
- `test-strategy`: aligned output table.

## [0.11.0]

### Changed

- `unit-tests`: prove each test can fail; a test exposing a product bug is reported, not bent to the buggy output.

## [0.8.0]

Quality craft: test strategy, coverage-gap analysis, unit-test authoring.

### Skills

- **assertion-quality** — Review test assertions — assert behavior not implementation; kill snapshot/tautological checks; one reason-to-fail per test; improves existing tests, not authoring them (unit-tests).
- **coverage-gap** — Review a diff for missing test coverage; pairs every changed behavior with an existing test or a flagged gap plus a recommended layer; finds gaps, not authoring (unit-tests).
- **integration-contract** — Design integration/contract tests for a service boundary — consumer-driven contracts, stub-vs-hit, fixtures, failure modes. Boundary tests, not unit tests (unit-tests) or the plan (test-strategy).
- **test-smell** — Detect test smells/anti-patterns — over-mocking, fragile assertions, slow setup, flaky timing; flag each with its layer and a refactor. Reviews existing tests, not authoring them (unit-tests).
- **test-strategy** — Design a layered test strategy (pyramid) for a feature or repo; recommends unit/integration/e2e split and the cheapest set that covers the acceptance criteria. Plans layers; doesn't write tests.
- **unit-tests** — Author unit tests using the repo's existing framework; one test per behavior, no mocking of internal collaborators. Writes tests; not gap analysis (coverage-gap) or strategy (test-strategy).
