---
name: code-review
description: Review a code change for correctness, simplification, and missing tests; produces a structured review summary keyed to the diff.
---

# code-review

> Review a code change with two lenses: correctness (does it do what the PRD says?) and simplification (could it do the same with less?).

## When to use

- A workflow invokes `polymath-engineering:code-review` after `feature-dev`.
- The user says "review this", "look this over", "what would you change?".

## Inputs

- The diff under review (typically the current git diff or the file set from `feature-dev`).
- PRD + acceptance criteria for the change (preferred).
- Project conventions.

## Procedure

1. **Read the PRD's acceptance criteria.** Each criterion is a checkpoint the code must satisfy.
2. **Read the diff in dependency order** (config → models → core logic → API → UI).
3. **For each acceptance criterion**, verify a test exists that would fail if the corresponding code were broken. If not, flag as a missing test.
4. **Correctness pass:**
   - Off-by-one, signedness, encoding, time-zone.
   - Concurrency: races, ordering, atomicity.
   - Error paths: do they leave the system in a recoverable state?
   - Boundary: empty input, single element, max input.
5. **Simplification pass:**
   - Could two functions be one? (Only if one of them has no other caller.)
   - Are there unused parameters, branches, or imports?
   - Are abstractions premature?
   - Are comments restating what the code already says?
6. **Security smell check:**
   - User input directly in SQL, HTML, shell, paths.
   - Secrets in code or logs.
   - Missing AuthN / AuthZ on new endpoints.
7. **Test smell check:**
   - Tests asserting implementation details.
   - Tests that pass without the code change (mock theater).
   - Flaky test patterns (sleeps, time-of-day).

## Output

Structured summary keyed to the diff:

```text
Acceptance criteria coverage:
  - AC1: PASS — test at <file>:<line>
  - AC2: MISSING — no test for refund path

Correctness findings:
  - <file>:<line> — boundary: rate-limit window misses requests exactly at start

Simplification findings:
  - <file>:<line> — extracted helper has one caller; inline it

Security findings:
  - <file>:<line> — user-supplied path concatenated without normalization

Test smell findings:
  - <file>:<line> — assertion checks private member rather than observed behavior
```

No emoji, no praise filler. Findings only.

## Quality bar

- Every finding cites file:line.
- Every "MISSING" finding either nominates a missing test or proposes an alternative way to verify.
- No nit-style comments mixed in with correctness findings.
