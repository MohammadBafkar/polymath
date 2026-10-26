---
name: code-review
description: Review a code change for correctness, simplification, and missing tests; produces a structured review summary keyed to the diff. Reviews a diff; not test-gap hunting (coverage-gap).
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

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `conventions_docs`: read roles `review-checklist` plus the stack docs
  (`backend-stack`, `frontend-stack`, `database`) that match the diff;
  treat their Hard rules as review axes; surface `[VERIFY: …]` items only
  when they affect a finding.
- `skill_overrides["polymath-engineering:code-review"]`: read each
  `additional_context` file; apply each `additional_axes` entry as an
  extra review axis. Cite `conventions.code_review_checklist` in the
  review summary when set.

## Procedure

1. **Establish intent.** Read the PRD's acceptance criteria — each is a checkpoint the code must satisfy. No PRD? Derive intent from the PR description, linked issue, or commit messages, and state that assumption at the top of the review.
2. **Get the exact diff.** Review against the merge base, not a moving branch tip: `git diff $(git merge-base origin/<base> HEAD)` (default base: the remote's default branch), plus staged and unstaged changes when reviewing local work. Note untracked files the change depends on.
3. **Read the diff in dependency order** (config → models → core logic → API → UI), and read beyond it: for every changed signature, contract, or shared helper, open its callers. Many bugs live in the unchanged code that consumes the change.
4. **For each acceptance criterion**, verify a test exists that would fail if the corresponding code were broken. If not, flag it as a missing test.
5. **Correctness pass:**
   - Off-by-one, signedness, encoding, time-zone, null/empty handling.
   - Concurrency: races, ordering, atomicity, idempotency of retried paths.
   - Error paths: do they leave the system in a recoverable state? Resources (files, connections, locks) released on every path?
   - Boundary: empty input, single element, max input.
   - Compatibility: does it break existing callers, persisted data, or a public API/schema?
   - Performance on realistic sizes: N+1 queries, unbounded loops or memory, work inside hot paths.
6. **Simplification pass:**
   - Could two functions be one? (Only if one of them has no other caller.)
   - Are there unused parameters, branches, or imports?
   - Are abstractions premature?
   - Are comments restating what the code already says?
7. **Security smell check:**
   - User input directly in SQL, HTML, shell, paths.
   - Secrets in code or logs.
   - Missing AuthN / AuthZ on new endpoints; object-level checks on user-supplied IDs.
8. **Test smell check:**
   - Tests asserting implementation details.
   - Tests that pass without the code change (mock theater).
   - Flaky test patterns (sleeps, time-of-day).
9. **Verify before reporting.** For each correctness or security finding, trace a concrete input or path that triggers it. If you can't, downgrade it to a question. Separate issues the change introduced from pre-existing ones (report those last, as non-blocking).

## Output

Structured summary keyed to the diff:

```text
Verdict: REQUEST CHANGES   (1 blocker, 1 major, 2 minor)
Intent source: PRD docs/prds/rate-limit.md   (or: "derived from PR description")

Acceptance criteria coverage:
  - AC1: PASS — test at <file>:<line>
  - AC2: MISSING — no test for refund path

Correctness findings:
  - [blocker] <file>:<line> — boundary: rate-limit window misses requests exactly at start
    Trigger: request at t = window_start → counted in neither window.

Simplification findings:
  - <file>:<line> — extracted helper has one caller; inline it

Security findings:
  - <file>:<line> — user-supplied path concatenated without normalization

Test smell findings:
  - [minor] <file>:<line> — assertion checks private member rather than observed behavior

Pre-existing (not introduced by this change, non-blocking):
  - <file>:<line> — …
```

No emoji, no praise filler. Findings only.

## Quality bar

- Every finding cites file:line and carries a severity (blocker / major / minor).
- Every correctness/security finding names the input or path that triggers it; unproven suspicions are phrased as questions.
- Every "MISSING" finding either nominates a missing test or proposes an alternative way to verify.
- No nit-style comments mixed in with correctness findings; pre-existing issues are separated from introduced ones.
- One verdict: APPROVE, APPROVE WITH NITS, or REQUEST CHANGES.
