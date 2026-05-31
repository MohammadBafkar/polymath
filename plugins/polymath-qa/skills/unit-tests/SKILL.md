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
3. Avoid:
   - Mocking internal collaborators (mock only the boundaries you don't own — clock, network, filesystem).
   - Asserting on private attributes.
   - Time-of-day or random seeds without explicit injection.
   - "Helper test" that calls another test.

## Output

- Test files in the repo's conventional location.
- Each new test runs green when invoked through the repo's test command.
- A summary lists which behaviors are now covered and which (if any) still aren't.

## Anti-patterns to avoid

- Snapshot tests for behaviors that should have explicit assertions.
- "Should not throw" tests where a specific outcome is what matters.
- Parameterized tests where each case actually tests a different behavior — split them.
