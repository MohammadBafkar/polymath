---
name: write-plan
description: Write a project / change plan to docs/plans/<slug>.md from the canonical Plan template; What, Why, Approach, Work breakdown, Risks, Verification, Out of scope. The full plan doc, not a standalone WBS.
---

# write-plan

> Author a plan that is short, actionable, and explicit about what we are *not* doing.

## When to use

- A non-trivial change needs a written approach before implementation.
- A workflow invokes `polymath-planning:write-plan`.
- The user asks "what's the plan?".

## Inputs

- Title (required).
- Motivation: PRD path, problem statement, or ADR link.
- Constraints: timeline, team, dependencies.

## Procedure

1. Read [`Plan.md`](../../templates/Plan.md).
2. Compute slug from the title.
3. **Summary-first checkpoint.** Before writing the document, show a
   one-screen skeleton — the What in one sentence, the 3–5 approach
   phases, the locked decisions you'll honor, the top risk — and confirm
   direction. Cheaper to redirect a skeleton than a finished plan.
4. Draft `docs/plans/<slug>.md`:
   - **What** — outcome in one paragraph.
   - **Why** — link the PRD/ADR; quote the constraint that made this necessary.
   - **Approach** — 3–5 phases, not tasks.
   - **Locked decisions** — decisions already made (spike/ADR/owner, with
     source) that the plan must not relitigate.
   - **Work breakdown** — numbered, each step independently completable.
   - **Risks** — at least one risk with a mitigation.
   - **Verification** — observable signals or artifacts.
   - **Deferral registry** — wanted-but-deferred work, each entry with the
     condition that reopens it (never a bare "later").
   - **Out of scope** — explicit non-goals.
5. Stop. Do not start implementation in the same skill turn.

## Quality bar

- Plan ≤ 60 lines total. If it grows past that, decompose the scope.
- Every step in the work breakdown is observable from the outside (a file exists, a test passes, a deploy goes out).
- The "Out of scope" section has at least one entry.
- Every deferral names its revisit condition; every locked decision names
  its source.

## Output

- File: `docs/plans/<slug>.md`.
- Summary listing the phase count and risk count.
