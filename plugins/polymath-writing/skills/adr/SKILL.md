---
name: adr
description: Write an Architecture Decision Record (Michael Nygard format) to docs/adrs/NNNN-<slug>.md; frontmatter validated by the ADR artifact schema. Records a made decision, not a proposal to debate (rfc).
---

# adr

> Capture a decision so future contributors know what was decided and why. ADRs are immutable once accepted — supersede them instead of editing.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A decision is being made that future readers will need to understand.
- A workflow invokes `polymath-writing:adr`.
- The user says "write an ADR".

## Inputs

- Title (required).
- Context: PRD link, problem statement, alternatives considered.

## Procedure

1. Find the repo's existing ADR directory first (`docs/adrs/`, `docs/adr/`, `doc/architecture/decisions/`, an `.adr-dir` file from adr-tools) and use it; create `docs/adrs/` only if none exists. Determine the next number: the highest existing `NNNN-` prefix + 1 (default 0001).
2. **Slug** from the title: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
3. Read [`ADR.md`](../../templates/ADR.md).
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
- Never edit an accepted ADR's decision. Supersede it with a new ADR; the only change to the old one is its status line (`Superseded by NNNN`), so readers can follow the chain.

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
