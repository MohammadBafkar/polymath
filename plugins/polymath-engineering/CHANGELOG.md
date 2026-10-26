# Changelog — polymath-engineering

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 4 analytical, 1 deterministic — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `verify-change` is deterministic (fixed order, fixed status vocabulary, real counts).
- `feature-dev`: exact summary shape; in an unattended run, missing acceptance criteria fail the step instead of being invented.
- `tech-debt-management`: one ranking formula (interest ÷ principal × roadmap factor, fixed tie-break) and an exact register shape.

## [0.11.0]

### Changed

- `code-review`: intent fallback when there is no PRD, merge-base diff, callers of changed code, compatibility/perf/resource checks, verify-before-report, severities and a verdict, pre-existing issues separated.
- `feature-dev`: baseline test run before changes; green never comes from weakening, skipping, or special-casing tests; repo conventions no longer point at the marketplace's `polymath-core:conventions`.
- `verify-change`: CI config and contributor docs as detection signals, lockfile-aware package manager (`stack.package_manager` now wired), build-only short-circuit, "0 tests collected" ≠ PASS, introduced vs pre-existing failures, flaky reporting.
- Localization preamble (code-review, feature-dev, verify-change) falls back to `.polymath/project.yaml` and ignores another repo's snapshot.

### Fixed

- `verify-change` no longer tells the model to include "tests"/"verified" so a `stepSummaryMatches` gate passes — summaries report what actually ran.

## [0.8.0]

Engineering craft: TDD feature-dev loop, code review, change verification, codebase orientation, tech-debt management.

### Skills

- **code-review** — Review a code change for correctness, simplification, and missing tests; produces a structured review summary keyed to the diff. Reviews a diff; not test-gap hunting (coverage-gap).
- **feature-dev** — Build the smallest safe change satisfying a PRD/acceptance criteria via a TDD loop; produces a code diff plus tests.
- **read-code** — Orient quickly in an unfamiliar codebase area; produce a one-page map of structure, entry points, and the most likely place a change should land.
- **tech-debt-management** — Triage technical debt — classify (deliberate/accidental), quantify principal vs interest, and sequence paydown against feature work with a payback rationale.
- **verify-change** — Run repository-appropriate verification (build, lint, type-check, tests) on the changed files; summarize pass/fail per category.
