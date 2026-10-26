---
name: feature-dev
description: Build the smallest safe change satisfying a PRD/acceptance criteria via a TDD loop; produces a code diff plus tests.
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
- Repository conventions: `CONTRIBUTING.md` / `AGENTS.md` / `CLAUDE.md` plus the project context's `conventions_docs` (below). (`polymath-core:conventions` is the *Polymath marketplace's* authoring guide — not this repo's conventions.)

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `conventions_docs`: read roles `backend-stack` / `frontend-stack` /
  `shared-libraries` as relevant; the Architecture directive
  (target-vs-legacy) constrains where new code lands; Hard rules are
  guardrails, not suggestions.

## Procedure

1. **Orient.** Read the PRD and the surrounding code area. If unfamiliar, invoke the `read-code` skill first.
2. **Baseline.** Run the relevant existing tests before changing anything and record what already fails. Pre-existing failures are reported, not "fixed" as part of this change and not blamed on it.
3. **Pick the smallest acceptance criterion** that is independently testable.
4. **Write a failing test** for that criterion. Use the project's test framework. If no test infrastructure exists, surface this and ask before scaffolding.
5. **Run the test.** Confirm it fails for the right reason (assertion failure, not import error).
6. **Implement the minimum code** to pass that test. No speculative generality.
7. **Run all relevant tests.** Confirm green — and that the baseline's pre-existing failures are unchanged, not newly broken.
8. **Refactor only the new code.** Inline obvious duplication; do not refactor surrounding code.
9. **Repeat 3–8** for the next acceptance criterion.
10. **Stop when acceptance criteria are met.** Do not invent additional features. Hand off to `verify-change` for lint/type-check/full verification.

## Quality bar

- Each commit (or logical chunk) keeps tests green.
- No dead code, no half-finished alternatives, no comments narrating the change.
- No new dependencies without an explicit ADR (surface as an open question rather than adding one silently).
- Green comes from the implementation, never from weakening the tests: no deleted or loosened assertions, skipped/disabled tests, special-cased test inputs, or edited expected values to match buggy output.
- Test names describe the behavior under test, not the implementation.

## Output

- A code diff that satisfies the listed acceptance criteria.
- Tests (unit or integration) co-located per repo conventions.
- A short summary listing files changed and behaviors covered.

## Anti-patterns to avoid

- Implementing behavior not in the PRD ("while I was in here…").
- Speculative error handling for cases that cannot occur. (Failure modes the change itself introduces — I/O, network, invalid input at a trust boundary — still get handled.)
- Making a red test pass by editing the test instead of the code.
- Refactoring code outside the change set.
- Adding feature flags or compatibility shims when a direct change suffices.
