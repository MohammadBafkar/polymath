---
name: prioritize
description: Prioritize a backlog or feature set — RICE, WSJF/cost-of-delay, MoSCoW, Kano, value-vs-effort 2x2, Now/Next/Later; exposes value/effort/confidence inputs, never an opaque score.
---

# prioritize

> Rank a set of candidate items with an explicit, inspectable method — and show the inputs, not just the verdict. A prioritization no one can challenge is not a prioritization.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A backlog, roadmap, or feature set needs an ordering and the team is arguing from gut feel.
- The user asks "what should we do first / next?", "rank these", or "is this worth it vs that?".
- A workflow invokes `polymath-planning:prioritize`.

This is the *ranking* step. It is not estimation (`polymath-planning:estimate`), task breakdown (`polymath-planning:work-breakdown`), or story slicing (`polymath-product:decompose-epic`) — prioritize consumes their outputs.

## Inputs

- The candidate items (required) — features, bugs, bets, epics.
- Per-item signals, as available: value/impact, reach, effort/cost, confidence, time-criticality, dependencies.
- A chosen method, or let the procedure pick one from the signals present.
- Missing signals are never invented: a number you had to guess is written with a trailing `?` (`2000?`); an item with no basis for an input at all is listed under "Not scored — needs data" instead of being scored.

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

1. **Gather signals.** List each item with the inputs the chosen method needs, in the same units across items. Mark guesses with `?`.
2. **Pick the method** per the table; state why in one line.
3. **Score RICE and WSJF with the bundled script — never by hand.** It shows every input beside the score, ranks with a fixed tie-break (RICE: higher confidence, then lower effort; WSJF: higher cost of delay, then smaller job; then input order), flags confidence ≤ 50%, and re-scores every guessed input at ×0.5 and ×2 to show whether the rank survives:

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/prioritize/scripts/score.py" --method rice <<'CSV'
   item,reach,impact,confidence,effort
   SSO login,2000?,2,80,4
   CSV export,1000,1,100,1
   CSV
   ```

   WSJF columns: `item,value,time_criticality,risk_reduction,job_size`. Paste the table and flags verbatim. **MoSCoW / Kano / 2×2** are categorical: give each item its category plus the one-line evidence for it; order within a category by input order.
4. **Cut a Now / Next / Later** boundary on the ranked list and say what each horizon is *not* committing to.
5. **Slug** from the backlog or area name: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
6. Write `docs/prioritization/<slug>.md`.

## Output

`docs/prioritization/<slug>.md`, in this shape:

```markdown
# Prioritization: Q3 product backlog

Method: RICE — product backlog with reach data for every item.

Method: RICE  (4 items; `?` = guessed input; `=` = same score as the row above, order set by the tie-break)

| Rank | Item | reach | impact | confidence | effort | score |
|---|---|---|---|---|---|---|
| 1 | CSV export | 1,000 | 1 | 100% | 1 | 1,000 |
| 2= | Dark mode | 4,000 | 0.5 | 100% | 2 | 1,000 |
| 3 | SSO login | 2,000? | 2 | 80% | 4 | 800 |
| 4 | Bulk refunds | 500 | 3 | 50% | 2 | 375 |

Flags:
- LOW CONFIDENCE (50%): Bulk refunds — rank rests on speculation.
- SSO login: guessed reach; rank moves 1–3 at ×0.5 / ×2 — needs evidence before it is committed.

## Now / Next / Later
- Now: CSV export, Dark mode — not committing to dates beyond this sprint.
- Next: SSO login — not committed until reach is measured (rank is guess-dependent).
- Later: Bulk refunds — directional; not committing that it ships.

## Not scored — needs data
- (none)

## Assumptions that would reorder this
- SSO reach of 2,000/quarter (guessed): at 1,000 it stays 3rd (score 400); at 4,000 it leads (1,600).
```

## Quality bar

- Every score shows the inputs that produced it; no opaque composite number.
- Confidence is surfaced per item; a high score built on low confidence is flagged, not hidden.
- The ranking names the 1–2 assumptions that would most change the order if wrong.
- Output states what `Next` and `Later` are explicitly *not* committing to yet.

## Anti-patterns

- A single composite score with no visible inputs (uncheckable; reads as objective when it is not).
- Computing or re-ordering RICE/WSJF scores by hand instead of pasting the script's table.
- Inventing reach/effort/impact numbers to fill the formula instead of marking them as guesses.
- Ranking without a confidence column, so a precise-looking order rests on speculation.
- Doing estimation or task breakdown here instead of consuming those skills' outputs.
