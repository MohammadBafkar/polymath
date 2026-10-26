---
name: architecture-doc
description: Write a C4-style architecture document; System Context + Containers (+ Components when interesting) with mermaid diagrams. Describes structure, not a decision (adr) or proposal (rfc).
---

# architecture-doc

> Author a C4-style architecture doc. Layers used: System Context (L1), Containers (L2), Components (L3 when interesting). L4 (code) is omitted by default.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new system needs an architecture doc.
- An existing doc is stale and someone is about to read it.
- A workflow needs to capture the design before significant new work.

## Inputs

- The system (required): its name, and the code/infra to read — services, IaC, deployment manifests, existing diagrams.
- The audience and the decisions the doc must ground (optional, default: new engineers and on-call).
- Related ADRs and the PRD (optional). Every container and relationship comes from what you read; anything inferred but unconfirmed is marked `[VERIFY]`.

## Procedure

1. Read [`Architecture-doc.md`](../../templates/Architecture-doc.md).
2. **Summary-first checkpoint.** Show a one-screen skeleton — the
   system's purpose in one sentence, the L2 container list, the 2–3
   architectural decisions the doc will defend — and confirm direction
   before drafting six sections of prose.
   Unattended run (workflow step, subagent): nobody can confirm — skip the
   wait, write the document, and open the summary with the skeleton.
3. Draft `docs/architecture/<system>.md` (`<system>` = the system name lowercased, each run of characters outside `a-z0-9` replaced with `-`; an existing doc is updated in place, showing the diff):
   - **Purpose** — who reads this, what decisions it grounds.
   - **System context (L1)** — the system in relation to users + external systems. Mermaid diagram.
   - **Containers (L2)** — deployable units (services, databases, queues, frontends). Table + diagram.
   - **Components (L3)** — only if the most interesting container has enough internal structure to warrant it.
   - **Cross-cutting concerns** — AuthN/Z, observability, data classification, failure modes.
4. Link related ADRs and the originating PRD.

## Quality bar

- L1 + L2 diagrams are present and current.
- The container table cites tech and responsibility per container.
- L4 (code) is **not** present unless the user asked for it. C4 says skip it by default.
- Cross-cutting concerns are concrete (named systems, not "we use observability").

## Output

- File: `docs/architecture/<system>.md`.
- Summary listing the C4 levels included and the number of containers documented.
