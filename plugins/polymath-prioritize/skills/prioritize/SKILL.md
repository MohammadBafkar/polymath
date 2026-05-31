---
name: prioritize
description: Prioritize a backlog or feature set — RICE, WSJF/cost-of-delay, MoSCoW, Kano, value-vs-effort 2x2, Now/Next/Later; exposes value/effort/confidence inputs, never an opaque score.
---

# prioritize

> Rank a set of candidate items with an explicit, inspectable method — and show the inputs, not just the verdict. A prioritization no one can challenge is not a prioritization.

## When to use

- A backlog, roadmap, or feature set needs an ordering and the team is arguing from gut feel.
- The user asks "what should we do first / next?", "rank these", or "is this worth it vs that?".
- A workflow invokes `polymath-prioritize:prioritize`.

This is the *ranking* step. It is not estimation (`polymath-planning:estimate`), task breakdown (`polymath-planning:work-breakdown`), or story slicing (`polymath-product:decompose-epic`) — prioritize consumes their outputs.

## Inputs

- The candidate items (required) — features, bugs, bets, epics.
- Per-item signals, as available: value/impact, reach, effort/cost, confidence, time-criticality, dependencies.
- A chosen method, or let the procedure pick one from the signals present.

## Method selection

Pick the lightest method the available signals support:

| Method | Use when | Score |
| --- | --- | --- |
| **Value-vs-effort 2×2** | Few items, rough signals, need a fast cut | quadrant: do / schedule / maybe / drop |
| **RICE** | Product backlog with reach + impact data | `(Reach × Impact × Confidence) / Effort` |
| **WSJF** | Flow/agile, cost-of-delay matters | `Cost of Delay / Job Size`, CoD = value + time-criticality + risk-reduction |
| **MoSCoW** | Fixed scope/deadline, must agree on the floor | Must / Should / Could / Won't (this round) |
| **Kano** | Feature mix; satisfaction vs presence | Basic / Performance / Delight / Indifferent |

When in doubt, default to RICE for product backlogs and WSJF when delivery sequencing (not just value) is the question.

## Procedure

1. **Gather signals.** List each item with the inputs the chosen method needs. Mark any input that is a guess; do not silently invent reach/effort numbers.
2. **Pick the method** per the table; state why in one line.
3. **Score every item** showing the component inputs alongside the result — never a bare number. Use the same units across items.
4. **Rank**, then **sanity-check**: flag ties, low-confidence rows (confidence ≤ 50%), and any item whose rank depends entirely on a guessed input.
5. **Cut a Now / Next / Later** boundary and say what each horizon is *not* committing to.
6. Write `docs/prioritization/<slug>.md`: the method + rationale, the scored table (inputs visible), the Now/Next/Later cut, and the assumptions the ranking rests on.

## Output

`docs/prioritization/<slug>.md` — method, scored table with inputs, Now/Next/Later, assumptions.

## Quality bar

- Every score shows the inputs that produced it; no opaque composite number.
- Confidence is surfaced per item; a high score built on low confidence is flagged, not hidden.
- The ranking names the 1–2 assumptions that would most change the order if wrong.
- Output states what `Next` and `Later` are explicitly *not* committing to yet.

## Anti-patterns

- A single composite score with no visible inputs (uncheckable; reads as objective when it is not).
- Inventing reach/effort/impact numbers to fill the formula instead of marking them as guesses.
- Ranking without a confidence column, so a precise-looking order rests on speculation.
- Doing estimation or task breakdown here instead of consuming those skills' outputs.
