---
name: rfc
description: Draft a lightweight design RFC to docs/rfcs/<slug>.md; Summary, Motivation, Detailed design, Drawbacks, Alternatives, Unresolved questions. A proposal to debate, not a recorded decision (adr).
---

# rfc

> Lightweight design RFC. Use for changes large enough to need group review but not big enough to need ADR-grade permanence.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A non-trivial design needs feedback before implementation.
- The user says "let's write an RFC for this".

## Inputs

- Title and the change being proposed (required). None: ask; never draft an RFC around an invented change.
- Motivation evidence (optional but expected): incidents, metrics, user reports. Absent: the Motivation section says `[TBD: evidence]` and the summary flags the RFC as not ready for review.
- Alternatives already discussed and related ADRs/PRDs (optional).

## Procedure

1. Read [`RFC.md`](../../templates/RFC.md).
2. **Slug** from the title: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
3. **Summary-first checkpoint.** Show a one-screen skeleton — the
   change in one sentence, the motivation evidence, the alternatives
   you'll compare — and confirm direction before the full draft.
   Unattended run (workflow step, subagent): nobody can confirm — skip the
   wait, write the document, and open the summary with the skeleton.
4. Draft `docs/rfcs/<slug>.md`:
   - **Summary** — one paragraph; what changes for callers.
   - **Motivation** — concrete evidence, not "we should probably".
   - **Detailed design** — enough that an implementer can build from it.
   - **Drawbacks** — honest cost; what we commit to maintaining.
   - **Alternatives** — what we considered and why this is the chosen path.
   - **Unresolved questions** — must be resolved before merge or deferred explicitly.

## Quality bar

- "Motivation" cites at least one piece of concrete evidence.
- "Drawbacks" is non-empty.
- "Unresolved questions" is present (even if "none").
- ≤ 200 lines total. If it's larger, split into multiple RFCs.

## Output

- File: `docs/rfcs/<slug>.md`.
- Summary listing the open question count.
