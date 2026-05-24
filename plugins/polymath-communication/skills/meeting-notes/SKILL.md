---
name: meeting-notes
description: Capture meeting notes in three sections — decisions made, action items with owners + dates, open questions; never a transcript.
---

# meeting-notes

> Notes are not a transcript. Three fixed sections: decisions, actions, open questions. Anything else is conversation foam.

## When to use

- A meeting just ended and you want notes that someone who wasn't there can act on.
- A workflow's standup / planning step needs structured notes for tracking.

## Inputs

- Meeting context (date, attendees, topic).
- Your raw notes / transcript / recollection.

## Procedure

1. Skip "background", "discussion", "context" sections. Those belong in the underlying docs.
2. Capture three sections only:
   - **Decisions made** — each as one sentence with the decision verb in front ("Decided to ship X behind a flag at 10%"). Name the decision-owner.
   - **Action items** — each with owner (a person, not "the team"), due date, and the observable outcome ("@alice — by 2026-05-31 — opens PR for rate-limit middleware").
   - **Open questions** — what we agreed we don't know, with who is going to resolve it.
3. Conflicts of memory: write what was concretely said. If two people remember differently, log the disagreement explicitly rather than picking one.
4. Distribute within 24 hours. Notes that arrive 3 days later get ignored.

## Output

```text
Meeting notes: <topic> — <date>

Attendees: …

Decisions
  - Decided to <verb + concrete> (owner: @alice).
  - Decided to defer <X> until <when> (owner: @bob).

Actions
  - @alice — 2026-05-31 — opens PR for rate-limit middleware.
  - @bob — 2026-06-07 — files Snyk-triage tickets for the 3 critical findings.

Open questions
  - Are we paying for Stripe's new tier? Owner: @carol; resolve by 2026-05-28.
```

## Quality bar

- Three sections, no more.
- Every action item has owner + date + observable outcome.
- Decision section starts with a verb.
- No "we discussed …" entries.

## Anti-patterns to avoid

- Transcripts. They get nobody to do anything.
- "@team will look into it." Pick a person.
- Action items with no date.
- Burying a decision inside a paragraph. Decisions are top-level.
