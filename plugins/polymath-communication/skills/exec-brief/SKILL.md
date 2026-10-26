---
name: exec-brief
description: Write a BLUF exec brief — TL;DR first, one recommendation (not menu of three), unambiguous ask, "what if no" cost stated.
---

# exec-brief

> Bottom Line Up Front. One page. The exec stops reading after the TL;DR
> and walks away with the right answer.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- An exec or stakeholder needs a decision and you want them ready in <5 min reading.
- A long doc needs a one-pager to drive the meeting.
- A workflow's "escalation" step needs an exec-shaped artifact.

## Inputs

- Title / topic.
- Audience (specific person or role).
- The ask — what does "yes" mean concretely.
- Underlying source material (PRD, ADR, data).

## Procedure

1. Read [`Exec-brief.md`](../../templates/Exec-brief.md) (materialized).
2. **Slug** from the title: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
3. Draft `docs/briefs/<slug>.md`:
   - **TL;DR**: state the decision / ask / recommendation in one paragraph. Not "we want to talk about X" — what's the answer?
   - **What's happening**: ≤ 2 paragraphs of evidence. Cite metrics, customer quotes, deadlines. No background unless load-bearing.
   - **What we're recommending**: ONE option. Not a menu of three.
   - **Why this and not alternatives**: name the next-best alternative and the trade-off you accept by not picking it.
   - **What we need from you**: the unambiguous ask + deadline.
   - **If yes / if no**: short consequences. Honest, not hyperbolic.
4. Length target: ≤ 1 page.
5. Never invent numbers, quotes, or dates — every figure traces to the source material; a missing one is written `[TBD: <what>]` and listed in the summary.

## Quality bar

- TL;DR makes sense if the reader stops there.
- ONE recommendation, not a menu.
- Ask is concrete ("approve $50k for Q3 work" not "align on direction").
- "What if no" cost stated honestly.
- No background section. Background goes in references.
- Every number and quote traces to the source material; gaps are marked `[TBD]`, not filled.

## Output

- File: `docs/briefs/<slug>.md`.
- Summary: one-line headline (the TL;DR's first sentence).

## Anti-patterns to avoid

- "Here are three options, what do you think?" — that's a discussion doc, not an exec brief.
- TL;DR that's a meta-description ("This doc covers X").
- Hyperbolic "if no" ("the company will fail"). Be specific.
- 4 pages. Cut to one.
