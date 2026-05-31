---
name: rfc
description: Draft a lightweight design RFC to docs/rfcs/<slug>.md; Summary, Motivation, Detailed design, Drawbacks, Alternatives, Unresolved questions. A proposal to debate, not a recorded decision (adr).
---

# rfc

> Lightweight design RFC. Use for changes large enough to need group review but not big enough to need ADR-grade permanence.

## When to use

- A non-trivial design needs feedback before implementation.
- The user says "let's write an RFC for this".

## Procedure

1. Read [`RFC.md`](../../templates/RFC.md).
2. Compute slug from the title.
3. Draft `docs/rfcs/<slug>.md`:
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
