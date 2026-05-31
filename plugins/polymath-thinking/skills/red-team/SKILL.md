---
name: red-team
description: Adversarially challenge a plan, design, or PRD; produces a list of objections with the strongest case the proposer hasn't refuted. Challenges a plan/PRD, not pre-launch failures (pre-mortem).
---

# red-team

> Take the opposite side. Find the strongest objections the proposer hasn't refuted.

## When to use

- After a plan/PRD/ADR draft, before commit.
- A workflow's `reviewPR` invokes this as a fanout sibling for the "simplification + challenge" axis.
- The user says "what could go wrong?" or "play devil's advocate".

## Inputs

- The artifact under review (plan, PRD, design doc, diff).

## Procedure

1. Identify the load-bearing assumptions in the artifact. List them explicitly.
2. For each, ask:
   - What would make this assumption false?
   - What evidence would we see if it were false today?
   - What is the strongest case against the chosen approach?
3. Surface unstated alternatives the artifact ignores.
4. Quote one specific line from the artifact for each objection — no general complaints.

## Output

```text
Red-team: <artifact>

Assumption surface:
  A1: <quoted line>  ("we assume …")
  A2: <quoted line>
  …

Objections:
  - A1 fails if … . Evidence we'd see today: … . Strongest counter-approach: ….
  - A2 fails if … . …

Ignored alternatives:
  - <approach the artifact didn't consider>: …
  - …

Recommendation:
  Either address objections N, M directly in the artifact or accept the residual risk explicitly.
```

## Quality bar

- Objections are specific to *this* artifact, not generic ("scaling concerns").
- Each objection cites the line it targets.
- Don't soften — the proposer's job is to refute, not the red team's job to be polite.
