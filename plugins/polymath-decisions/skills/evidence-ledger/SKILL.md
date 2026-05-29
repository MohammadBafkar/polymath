---
name: evidence-ledger
description: Separate facts from assumptions from unknowns for a decision; per unknown name confidence, the evidence that would resolve it, and how the recommendation flips; mark reversibility.
---

# evidence-ledger

> Make incomplete information explicit instead of papering over it. The output is
> a ledger that names what you know, what you are assuming, and what you do not
> know — and for each unknown, what evidence would change the answer.

## When to use

- A decision must be made with incomplete information and the gaps need to be named, not hidden.
- A workflow step needs an auditable record of assumptions before options are compared.
- The user asks "what are we assuming here?" or "what would change our mind?".

## Inputs

- The decision or question (one sentence).
- Whatever is currently known: docs, data, prior decisions, constraints.

## Procedure

1. Compute the slug from the decision.
2. Draft `docs/decisions/<slug>-evidence.md`:
   - **Facts** — things established by evidence. Cite the source (doc, metric, code path) per fact.
   - **Assumptions** — things being treated as true without proof. Each is a one-liner the reader could challenge.
   - **Unknowns** — a table, one row per open question:

     | Unknown | Best guess | Confidence | Evidence that resolves it | How the answer flips |
     | --- | --- | --- | --- | --- |

     Confidence is low / medium / high. "How the answer flips" states the
     decision that becomes right if the evidence comes back the other way.
   - **Reversibility** — classify the decision: one-way door (hard/expensive to
     undo) or two-way door (cheap to revise). Then state whether it is cheaper to
     decide-now-and-revise or to wait for the highest-value unknown to resolve.
   - **Bottom line** — one or two sentences: can we decide now under stated
     assumptions, or is a specific piece of evidence a hard blocker?

## Quality bar

- Facts cite a source; assumptions do not masquerade as facts.
- Every unknown names both the evidence that resolves it AND how the recommendation flips — an unknown with no decision impact is noise, drop it.
- Reversibility is stated explicitly; a one-way door with low-confidence unknowns is flagged as decide-with-caution.
- The ledger does not recommend an option — it equips the comparison that follows (e.g. `polymath-decisions:tradeoff-matrix`).

## Output

- File: `docs/decisions/<slug>-evidence.md`.
- One-line summary: count of facts / assumptions / unknowns and the single
  highest-value piece of missing evidence.

## Anti-patterns to avoid

- Listing unknowns with no resolving evidence or no decision impact.
- Treating a confident assumption as a fact.
- Burying a one-way-door irreversibility in prose instead of flagging it.
