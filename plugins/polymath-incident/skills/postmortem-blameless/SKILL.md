---
name: postmortem-blameless
description: Write a blameless postmortem to docs/postmortems/<incident-id>.md; frontmatter validated by the Postmortem artifact schema.
---

# postmortem-blameless

> Author a blameless postmortem. Output is `docs/postmortems/<incident-id>.md` whose frontmatter passes the `Postmortem` artifact schema.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- An incident has been resolved and the team wants to learn from it.
- A workflow's "after sev1/2" step (`respondToIncident`, `incidentRetroToActions`) triggers postmortem authoring.

## Inputs

- The incident timeline (from the scribe's notes / Slack channel export / paging tool).
- Impact data (affected users, duration, revenue if known).
- The triage record (`incident-triage` output).

## Project localization

Before the procedure, resolve the project snapshot —
`${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-core/project-context.json`
(ignore it if its `_meta.source` belongs to another repo; absent → read
`.polymath/project.yaml` directly; neither → built-in defaults). Then apply
(contract: `polymath-core:project-context`):

- `prompts.postmortem_template`: when set, use that file as the
  postmortem template instead of the catalog default.

## Procedure

1. Read [`Postmortem.md`](../../templates/Postmortem.md).
2. Compute `incident_id` (e.g. `IC-2026-09`) and slug.
3. Draft `docs/postmortems/<incident-id>.md`:
   - **Summary** — one paragraph, plain language.
   - **Impact** — users affected, revenue (or "none observable"), internal impact.
   - **Timeline** — UTC, one row per significant event, each traced to a source (alert, log, chat message, deploy record). A gap stays a visible gap (`[gap: 14:10–14:25, no record]`) — never fill it with a plausible-sounding event.
   - **Contributing factors** — incidents rarely have one root cause. Apply `polymath-thinking:5-whys` per factor; cite evidence; land each on a system property.
   - **What went well / poorly / where we got lucky** — equal weight.
   - **Action items** — each with owner (team), due date, tracking link.
   - **Blameless statement** — explicit; names only as roles.
4. Frontmatter satisfies the `Postmortem` artifact schema: `artifact: Postmortem`, `incident_id`, `severity`, `status`, `facilitator`, `occurred`, `resolved`, `blameless: true`.

## Quality bar

- Root cause is a system property (process, structure, incentive). Not "Alice clicked the wrong button".
- Every action has a team owner, a date, and a tracking link.
- "What went poorly" is non-empty.
- Names appear as roles unless the person opted in.
- No defensive language ("we should have known" — describe what was knowable instead).

## Output

- File: `docs/postmortems/<incident-id>.md`.
- Summary: severity, duration, action-item count, root-cause one-liner.

## Workflow validation

```yaml
mustPass:
  - id: postmortem-valid
    type: artifactValid
    path: docs/postmortems/${inputs.incident_id}.md
    artifact: Postmortem
```
