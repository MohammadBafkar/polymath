---
name: adr
description: Write an Architecture Decision Record (Michael Nygard format) to docs/adrs/NNNN-<slug>.md; frontmatter validated by the ADR artifact schema.
---

# adr

> Capture a decision so future contributors know what was decided and why. ADRs are immutable once accepted — supersede them instead of editing.

## When to use

- A decision is being made that future readers will need to understand.
- A workflow invokes `polymath-writing:adr`.
- The user says "write an ADR".

## Inputs

- Title (required).
- Context: PRD link, problem statement, alternatives considered.

## Procedure

1. Determine the next ADR number: scan `docs/adrs/` for the highest existing `NNNN-` prefix and add 1. Default to 0001 if the directory is empty.
2. Compute slug from the title.
3. Read [`ADR.md`](../../templates/ADR.md) (materialized from `shared/templates/ADR.md`).
4. Draft `docs/adrs/NNNN-<slug>.md`:
   - **Status** — proposed (default) or accepted, depending on context.
   - **Context** — quote the constraint that forced the decision.
   - **Decision** — one sentence, then enough detail to be implementable.
   - **Consequences** — positive, negative, neutral. Be honest about trade-offs.
   - **Alternatives considered** — at least two, each with a rejection reason.
5. Frontmatter must satisfy the `ADR` artifact schema: `artifact: ADR`, `title`, `status` (enum), `deciders` (string or array), `date`.

## Quality bar

- One decision per ADR. If your decision implies others, write multiple linked ADRs.
- "Consequences/Negative" is non-empty — every decision has a cost.
- "Alternatives considered" lists at least two with concrete rejection reasons.
- Never edit an accepted ADR. Supersede it with a new one.

## Output

- File: `docs/adrs/NNNN-<slug>.md`.
- Summary listing the ADR number and the status.

## Workflow validation

```yaml
mustPass:
  - id: adr-valid
    type: artifactValid
    path: docs/adrs/${adr_number}-${workflow.slug}.md
    artifact: ADR
```
