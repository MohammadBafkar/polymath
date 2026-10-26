---
name: test-smell
description: Detect test smells/anti-patterns — over-mocking, fragile assertions, slow setup, flaky timing; flag each with its layer and a refactor. Reviews existing tests, not authoring them (unit-tests).
---

# test-smell

> Read an existing test suite the way a reviewer would — find the tests that will rot, mislead, or flake, and say how to fix each.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A test suite is slow, flaky, or brittle and you want the *causes*, not just a green/red.
- Reviewing a test file or test diff for quality (distinct from reviewing the production code).
- A workflow invokes `polymath-qa:test-smell`.

This scans *existing* tests. It does not write tests (`polymath-qa:unit-tests`), find untested behavior (`polymath-qa:coverage-gap`), or judge assertion strength specifically (`polymath-qa:assertion-quality`).

## Inputs

- The test files or test diff to review.
- Optionally the production code under test, to judge over-coupling.

## Smells to flag

- **Over-mocking** — mocking internal collaborators; the test asserts the mock, not behavior.
- **Fragile assertions** — asserting incidental output (full strings, ordering, timestamps) that breaks on unrelated change.
- **Eager / multi-behavior tests** — one test covering several behaviors; unclear reason-to-fail.
- **Slow setup** — per-test heavy fixtures, real I/O where a seam would do.
- **Flaky timing** — `sleep`, wall-clock, ordering, shared mutable state across tests.
- **Test interdependence** — tests that pass only in a given order or share state.
- **Misplaced layer** — an integration concern tested as a unit (or vice versa).

## Procedure

1. Read the tests; for each smell found, cite the test by name and the line/pattern.
2. Name the layer the test *should* live at (unit / integration / e2e) if misplaced.
3. Recommend a concrete refactor per finding (introduce a seam, narrow the assertion, hoist setup, remove the sleep).
4. Rank findings by blast radius (flake-causing > brittle > slow > cosmetic).

## Output

Findings ranked by blast radius (flake-causing > brittle > slow > cosmetic), then file order:

```text
Test smells: tests/ (38 tests, 5 findings)

1. FLAKY TIMING      tests/test_worker.py::test_job_retries  (line 22: time.sleep(2))
   layer: unit (correct)
   fix:   inject a fake clock; assert on the scheduled retry time, not wall time

2. INTERDEPENDENCE   tests/test_cart.py::test_checkout  (reads the cart created by test_add_item)
   fix:   create the cart in this test's own fixture

3. OVER-MOCKING      tests/test_refunds.py::test_refund  (mocks RefundRepository, an internal collaborator)
   layer: should be integration (real repository on a test DB)
   fix:   replace the mock with the repository on testcontainers postgres

4. FRAGILE           tests/test_report.py::test_render  (asserts the whole 2 KB HTML string)
   fix:   assert the three totals and the title only

5. SLOW SETUP        tests/conftest.py::db  (migrates a fresh DB per test, ~1.4 s each)
   fix:   session-scoped migration + per-test transaction rollback

No smell: 33 tests.
```

## Quality bar

- Every finding cites a specific test, not "the suite generally".
- Each finding pairs the smell with a concrete fix and the correct layer.
- Does not propose rewriting passing tests with no smell — churn is not a finding.
