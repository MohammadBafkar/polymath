---
name: perf-review
description: Write a perf review — evidence-anchored, calibrated against level expectations, no surprises; areas-for-growth section already heard from 1:1s.
---

# perf-review

> A perf review with new feedback in it is a manager failure, not a review. This skill writes the review that consolidates what's already been said in 1:1s.

## When to use

- A performance cycle is closing.
- A manager wants the writeup grounded in concrete evidence + level expectations.

## Inputs

- Employee + manager + cycle name (Q3 2026, H1 2026, etc.).
- Career ladder document for the employee's level (required — without this, the review is uncalibrated).
- 1:1 notes from the cycle (the evidence source).
- Cross-team feedback / 360s if collected.

## Procedure

1. Read [`Perf-review.md`](../../templates/Perf-review.md).
2. Write `docs/people/<employee>/perf-<cycle>.md`:
   - **Impact** — 3–5 outcomes with evidence (metric, shipped artifact, customer quote). Their role in each.
   - **How they worked** — quote specific incidents. "In <project>, X did <thing>, leading to <outcome>." Not "is a great collaborator".
   - **Strengths** — 2–3 strongest patterns, each with an example.
   - **Areas for growth** — 1–2 highest-leverage gaps. **Each must already be familiar from a 1:1.** If it would surprise the employee, hold it and have the 1:1 first; don't ship the surprise.
   - **Recommendation** — promote / exceeds / meets / below — anchored in the level expectations, not in heroics.
   - **Calibration notes** — own the biases (recency, halo, comparison to a differently-leveled peer).
3. Stop. The Employee response section is theirs to fill.

## Quality bar

- Every impact bullet cites evidence.
- Every "How they worked" bullet has a specific incident, not an adjective.
- Areas for growth: previously delivered in 1:1. Never new at review time.
- Recommendation rationale references the level expectations.

## Output

- File: `docs/people/<employee>/perf-<cycle>.md`.
- Summary listing the recommendation + the 1–2 growth areas.

## Anti-patterns to avoid

- Surprise feedback ("you also struggle with X" without a 1:1 paper trail). Worst manager move there is.
- Adjective dumps ("great communicator, collaborative, ownership"). Useless.
- Recommendation that doesn't reference the level ladder.
- Withholding the calibration note. If recency is biasing you, own it.
