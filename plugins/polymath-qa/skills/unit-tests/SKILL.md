---
name: unit-tests
description: Author unit tests using the repo's existing framework; one test per behavior, no mocking of internal collaborators. Writes tests; not gap analysis (coverage-gap) or strategy (test-strategy).
---

# unit-tests

> Author unit tests for behaviors a `coverage-gap` pass identified as MISSING (unit).

## When to use

- A workflow invokes `polymath-qa:unit-tests`.
- The user asks "write tests for this".
- `coverage-gap` listed `MISSING (unit)` items.

## Inputs

- The behavior list (from `coverage-gap` or a manual request).
- Repo conventions (test framework, layout, naming).

## Procedure

1. Detect the framework: `pytest`, `vitest`, `jest`, `xunit`, `go test`, etc.
2. For each behavior, write one test:
   - Name describes the behavior, not the implementation.
   - Arrange / Act / Assert blocks are visible.
   - One assertion per behavior; multiple `assert`s only when they describe the same observation.
3. **Prove each test can fail.** For a test written against existing code, temporarily break the behavior it protects (flip the condition, return the wrong value) and watch it fail, then restore. A test that stays green is vacuous — fix the assertion.
4. **If a new test fails because the code is wrong, report the bug** — don't change the assertion to match the buggy output. Mark the test as a known failure only if the user agrees (with a link to the bug).
5. Avoid:
   - Mocking internal collaborators (mock only the boundaries you don't own — clock, network, filesystem).
   - Asserting on private attributes.
   - Time-of-day or random seeds without explicit injection.
   - "Helper test" that calls another test.

## Output

```text
tests/test_refunds.py
  test_refund_rejects_negative_amount        PASS
  test_refund_above_balance_returns_409      PASS

Covered: 2 behavior(s)   Still uncovered: 0
Run: pytest tests/test_refunds.py   → green
```

- Test files in the repo's conventional location.
- Each new test runs green when invoked through the repo's test command.
- A summary lists which behaviors are now covered and which (if any) still aren't.

## Anti-patterns to avoid

- Snapshot tests for behaviors that should have explicit assertions.
- "Should not throw" tests where a specific outcome is what matters.
- Parameterized tests where each case actually tests a different behavior — split them.
