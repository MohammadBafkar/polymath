---
name: interview-guide
description: Write a Mom-Test-shaped interview guide for one research question; past behavior over hypothetical, specifics over generalities.
---

# interview-guide

> Author one interview guide for one research question. Output is `docs/research/<slug>-guide.md` ready to run.

## When to use

- A product or research question needs primary evidence.
- A team is about to ship a feature based on what people say they want; pull this skill instead.

## Inputs

- The research question (one sentence).
- The audience to recruit (role, segment, behavior).
- Optional: existing personas / prior interview notes.

## Procedure

1. Read [`Interview-guide.md`](../../templates/Interview-guide.md).
2. Compute the slug from the question.
3. Draft `docs/research/<slug>-guide.md`:
   - **Research question** — exactly one. Reject bundled questions; pick the most important and spin the others off.
   - **Recruit** — audience + 2-3 screener questions + target N (5–8).
   - **Past behavior block** — every question references a specific past instance ("Tell me about the last time …").
   - **Specifics block** — show-me-how questions; ask for the workaround.
   - **Signal-test block** — time/money cost, prior attempts, others involved.
   - **Avoid list** — copy verbatim into the guide so the interviewer doesn't drift.
4. The guide is **not** a script. It's a backbone. Note "follow whatever's interesting".

## Quality bar

- Every question references the past or asks for specifics. Zero hypotheticals.
- Recruit screener is included in the doc (not "we'll figure it out later").
- Target N ≥ 5. Conclusions from < 5 are vibes.
- Avoid-list is present.

## Output

- File: `docs/research/<slug>-guide.md`.
- Summary listing target N + recruit channel suggestions.

## Anti-patterns to avoid

- Asking "would you use a feature that …" (hypothetical).
- Asking how important something is on a 1–10 scale (rating bias; pre-disposes the answer to politeness).
- Pitching the product mid-interview.
- Single-shot interview ("N=1, here's what we learned"). Wait for the set.
