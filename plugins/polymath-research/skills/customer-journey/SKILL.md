---
name: customer-journey
description: Map one persona's path through one JTBD — stages, what they're doing/thinking/feeling, touchpoints, pain; mark evidence vs assumption.
---

# customer-journey

> One persona, one job-to-be-done, 5–7 stages. Multiple personas → multiple journeys; don't merge.

## When to use

- A team has a persona doc and wants to surface where in the user's flow they're losing.
- Funnel analytics show drop-off but the team doesn't know why.

## Inputs

- The persona doc (required).
- The job-to-be-done in JTBD form ("When <situation>, I want to <motivation>, so I can <outcome>.").
- Optional: existing funnel analytics.

## Procedure

1. Read [`Customer-journey.md`](../../templates/Customer-journey.md).
2. Compute slug from the JTBD.
3. Draft `docs/research/journeys/<slug>.md`:
   - **JTBD** — verbatim in the doc.
   - **Stages** — 5–7. User-perspective, not product features. Trigger → Search → Evaluate → Onboard → First success → Habit → Tell others is a good default.
   - **Per stage** — what they're doing, thinking/feeling, touchpoints, pain.
   - **Peak pain moments** — the 1–2 highest-drop-off stages. These are the leverage points.
   - **Evidence vs assumption** — mark every stage `✓ Evidence` (quote-supported) or `? Assumption` (guess).
   - **Improvements** — top 3 changes sized by impact, with the metric each would move.

## Quality bar

- Stages are user-perspective ("evaluating options"), not product-perspective ("uses comparison page").
- Every stage marked Evidence or Assumption. Assumption-heavy journeys are flagged for research before action.
- Peak pain moments named explicitly.
- One persona per journey. Multi-persona journeys are merged guesses.

## Output

- File: `docs/research/journeys/<slug>.md`.
- Summary listing the 2 peak pain moments + the top improvement.

## Anti-patterns to avoid

- Generic "AAARRR" funnel re-labeled as a journey. The stages must reflect this specific JTBD.
- Stages full of `? Assumption` shipped as if they were research.
- "Delight" stage added as a vanity step. If there's no evidence of delight, don't add it.
- Improvements sized by "ease" or "what we can ship next sprint" instead of impact.
