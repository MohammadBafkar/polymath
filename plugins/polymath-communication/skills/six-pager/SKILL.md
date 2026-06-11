---
name: six-pager
description: Author an Amazon-style six-page narrative — prose not bullets, tenets up front, FAQ at the end; the FAQ is where objections live.
---

# six-pager

> Prose narrative, ~1,800 words, read silently in the meeting room for the
> first 15–20 minutes. No slides. The FAQ is where the rigor lives.

## When to use

- A meeting needs a shared starting point that survives the loudest voice.
- A direction needs to be argued in writing before any of the alternatives are killed off.
- A workflow needs a substantive narrative artifact (not a one-pager).

## Inputs

- Title / topic.
- Audience.
- Underlying material (PRDs, data, prior decisions).

## Procedure

1. Read [`Six-pager.md`](../../templates/Six-pager.md).
2. Compute slug.
3. **Summary-first checkpoint.** Show a one-screen skeleton — the
   question being decided, the tenets, the recommendation in one
   sentence — and confirm direction before writing six pages.
4. Draft `docs/six-pagers/<slug>.md`:
   - **Introduction** — 1–2 paragraphs framing the question.
   - **Tenets** — 3–5 short sentences naming what's load-bearing. Tenets bind the rest of the doc.
   - **Current state** — evidence-based. Numbers, screenshots, customer quotes.
   - **Why now** — the trigger. Without it, urgency is ambient.
   - **Approach** — paragraphs, not bullets. Each paragraph makes one point.
   - **Risks and mitigations** — most likely failure + most damaging failure + mitigation each.
   - **Success measure** — one metric per 30 / 90 / 180-day window.
   - **What we need to decide today** — the concrete ask.
   - **Appendix: FAQ** — 5–8 hardest questions with paragraph answers. This is where the doc earns its keep.
5. Length target: 1,500–2,000 words.

## Quality bar

- Prose, not bullets, in the body. Bullets allowed in Tenets and Risks only.
- Tenets present and binding.
- "Why now" is concrete (a deadline, a metric inflecting, a regulatory shift).
- FAQ has 5+ questions; answers don't dodge.
- Word count 1,500–2,000.

## Output

- File: `docs/six-pagers/<slug>.md`.
- Summary: tenet count + FAQ count + word count.

## Anti-patterns to avoid

- Bullet-fested body. Forces shallow thinking.
- Tenets that read as platitudes ("we value quality"). Tenets are trade-offs — what you give up to honor them.
- Missing FAQ. Half the doc's value is the answers to the hard questions.
- Closing with "thoughts?" instead of a concrete ask.
