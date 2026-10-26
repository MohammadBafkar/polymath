---
name: runbook
description: Write or refresh an operational runbook for an alert/symptom; structured as TL;DR + Pre-checks + Steps + Verification + Rollback + Escalation.
---

# runbook

> Author or refresh a runbook so an on-call can resolve the situation without paging the author.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new alert exists without a runbook.
- An existing runbook is stale (last_reviewed > 6 months) or wrong.
- A workflow's incident step needs to update operational docs.

## Inputs

- Alert name or symptom (required).
- The system architecture (link the architecture doc if available).
- Previous incidents in this area.

## Procedure

1. Read [`Runbook.md`](../../templates/Runbook.md).
2. **Slug** from the alert/symptom name: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
3. Draft `docs/runbooks/<slug>.md`:
   - **When this runbook applies** — precise alert/symptom; link the alert definition.
   - **TL;DR** — 3 bullets (symptom, fastest mitigation, rollback).
   - **Pre-checks** — checklist of preconditions.
   - **Steps** — numbered with expected outcomes, copy-paste friendly.
   - **Verification** — how to confirm the system is healthy.
   - **Rollback** — how to reverse if the action makes things worse.
   - **Escalation** — when to page whom.
4. Every command, dashboard link, and alert name must be one you verified exists (in the repo, the alert definition, or with the owning team). An unverified step is marked `[VERIFY: …]` — an on-call following an invented command at 3 AM is worse than a gap. Destructive commands carry a warning line and a pre-check; no secrets in the runbook — reference where to fetch them.
5. Update `last_reviewed` in the frontmatter to today.

## Quality bar

- Every step has an expected outcome.
- Rollback is non-empty.
- Escalation names a team or rotation, not a person.
- TL;DR is genuinely 3 bullets — not a paragraph reformatted.

## Output

- File: `docs/runbooks/<slug>.md`.
- Summary listing step count and whether the runbook is new or refreshed.
