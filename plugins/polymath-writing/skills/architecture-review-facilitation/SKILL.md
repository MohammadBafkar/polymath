---
name: architecture-review-facilitation
description: Run an architecture review as a process — entry criteria, reviewer checklist, decision log, and follow-up actions — pairing the design artifact with a red-team pass.
---

# architecture-review-facilitation

> The artifact skills (`architecture-doc`, `rfc`, `adr`) produce *what* is
> reviewed. This skill runs the *review itself*: gate the entry, structure the
> session, capture decisions, and assign follow-ups so a review board is
> repeatable instead of a free-for-all.

## When to use

- A team holds (or should hold) architecture / design reviews and wants a consistent rubric.
- A design doc or RFC is ready and needs a structured challenge before sign-off.
- A workflow needs a facilitation + decision-capture step after a design is drafted.

## Inputs

- The design artifact under review: a `polymath-writing:architecture-doc` or `polymath-writing:rfc`.
- The reviewers and the decision owner.

## Procedure

1. **Entry criteria.** Refuse to start unless the artifact exists and states its
   context, the options considered, and the open questions. If it doesn't, send
   it back — point the author at `polymath-writing:architecture-doc` / `:rfc`.
2. **Reviewer checklist.** Walk a fixed rubric so reviews are comparable:
   correctness of the problem framing, the rejected alternatives, failure modes
   and blast radius, security/trust boundaries, operability, and reversibility.
3. **Adversarial pass.** Run `polymath-thinking:red-team` against the leading
   design — strongest unrefuted objection and the evidence that would reverse it.
   The author's job is to refute or accept residual risk, not to be defended from it.
4. **Decision log.** Record each decision with its rationale and who owns it. For
   any accepted architectural decision, capture it durably via `polymath-writing:adr`
   (status Proposed if the context is still uncertain).
5. **Follow-ups.** Every unresolved objection becomes an owned action with a
   due-before date, or an explicitly accepted residual risk. Write
   `docs/reviews/<slug>-arch-review.md`.

## Output

- File: `docs/reviews/<slug>-arch-review.md` — entry-criteria check, the rubric
  findings, the red-team objections, the decision log, and the follow-up actions.
- One-line summary: the verdict (approved / approved-with-conditions / sent-back)
  and the count of open follow-ups.

## Quality bar

- Entry criteria are enforced — an under-specified artifact is sent back, not reviewed.
- The rubric is the same every time, so reviews are comparable across designs.
- The red-team objections are recorded with their resolution (addressed or accepted-as-risk).
- Every follow-up has an owner and a date; accepted decisions land in an ADR.
- Composes the artifact, red-team, and ADR skills; does not re-author the design inline.
