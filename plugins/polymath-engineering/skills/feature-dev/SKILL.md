---
name: feature-dev
description: Implement the smallest safe change satisfying a PRD/acceptance criteria using a TDD loop; produces a code diff plus tests.
---

# feature-dev

> Implement the smallest safe change that satisfies a PRD's acceptance criteria using a test-driven loop.

## When to use

- The user says "implement this", "build this feature", "let's write the code".
- A workflow invokes `polymath-engineering:feature-dev`.
- A PRD or acceptance criteria exist and the next step is code.

## Inputs

- PRD path (preferred) or a concise problem statement.
- Existing acceptance criteria (preferred). If absent, surface that gap and pause.
- Repository conventions (loaded from `polymath-core:conventions` if installed).

## Procedure

1. **Orient.** Read the PRD and the surrounding code area. If unfamiliar, invoke the `read-code` skill first.
2. **Pick the smallest acceptance criterion** that is independently testable.
3. **Write a failing test** for that criterion. Use the project's test framework. If no test infrastructure exists, surface this and ask before scaffolding.
4. **Run the test.** Confirm it fails for the right reason (assertion failure, not import error).
5. **Implement the minimum code** to pass that test. No speculative generality.
6. **Run all relevant tests.** Confirm green.
7. **Refactor only the new code.** Inline obvious duplication; do not refactor surrounding code.
8. **Repeat 2–7** for the next acceptance criterion.
9. **Stop when acceptance criteria are met.** Do not invent additional features.

## Quality bar

- Each commit (or logical chunk) keeps tests green.
- No dead code, no half-finished alternatives, no comments narrating the change.
- No new dependencies without an explicit ADR (out of v0.1 scope; surface as an open question).
- Test names describe the behavior under test, not the implementation.

## Output

- A code diff that satisfies the listed acceptance criteria.
- Tests (unit or integration) co-located per repo conventions.
- A short summary listing files changed and behaviors covered.

## Anti-patterns to avoid

- Implementing behavior not in the PRD ("while I was in here…").
- Adding error handling for cases the PRD does not call out.
- Refactoring code outside the change set.
- Adding feature flags or compatibility shims when a direct change suffices.
