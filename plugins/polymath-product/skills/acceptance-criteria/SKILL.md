---
name: acceptance-criteria
description: Add or refine Given/When/Then acceptance criteria for a PRD; each criterion is independently testable and maps to a test case.
---

# acceptance-criteria

> Author or refine acceptance criteria for a feature. Output goes into the PRD's "Acceptance criteria" section.

## When to use

- After a PRD draft exists but acceptance criteria are vague.
- A workflow step invokes `polymath-product:acceptance-criteria`.
- A reviewer asks "what does done look like?".

## Inputs

- Path to the PRD (required) — usually `docs/prds/<slug>.md`.
- Optional: scope hint (small/medium) to size the criteria.

## Procedure

1. Read the PRD's **Problem**, **Goals**, **Requirements**.
2. For each requirement, produce 1–3 Given / When / Then statements:
   - **Given** — the precondition (user state, system state, inputs).
   - **When** — the trigger action.
   - **Then** — the observable outcome.
3. Cover happy path, at least one edge case, and at least one error path.
4. Update the PRD's **Acceptance criteria** section in place. Surface a unified diff to the user before committing the change.

## Quality bar

- Each criterion is independently testable.
- No criterion depends on internal implementation details ("the cache should expire") — describe observable behavior ("repeated requests within 10s should not double-charge").
- At least one negative criterion (error or rejection path) per feature.
- Criteria reference roles/inputs explicit in the PRD; do not invent new actors.

## Output

- Updated PRD with the **Acceptance criteria** section populated.
- Brief summary listing how many criteria were added or revised.
