---
name: acceptance-criteria
description: Draft or refine Given/When/Then acceptance criteria for a PRD; each criterion is independently testable and maps to a test case.
---

# acceptance-criteria

> Author or refine acceptance criteria for a feature. Output goes into the PRD's "Acceptance criteria" section.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

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

The PRD's **Acceptance criteria** section, one numbered block per requirement, in this shape:

```markdown
### R2 — Lock the account after repeated failed logins

AC-2.1 (happy path)
  Given a user with 4 failed login attempts in the last minute
  When they submit the correct password
  Then they are signed in and the failure counter resets to 0

AC-2.2 (error path)
  Given a user with 5 failed login attempts in the last minute
  When they submit any password
  Then the response is 429 with a Retry-After of 900 seconds, and no session is created

AC-2.3 (edge)
  Given the 15-minute lock has expired
  When the user submits the correct password
  Then they are signed in
```

Plus a one-line summary: criteria added / revised per requirement.
