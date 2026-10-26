---
name: forecast
description: Model a delivery date/scope as a probability range — reference-class, throughput/Monte-Carlo, cone of uncertainty; range forecasting from data, not per-item estimation (estimate).
---

# forecast

> "When will it be done?" deserves a probability, not a date. Forecast from how work has actually flowed, and quote a range with a confidence.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A delivery date / scope-by-date needs a defensible probabilistic answer, ideally from historical data.
- Someone is being pressured into a single-date commitment for multi-item work.
- A workflow invokes `polymath-planning:forecast`.

This forecasts *aggregate delivery under uncertainty*. It is not per-item three-point sizing (`polymath-planning:estimate`), task breakdown (`polymath-planning:work-breakdown`), or capacity planning (`polymath-sre:capacity-plan`).

## Inputs

- The question (required): remaining scope in items ("when?") or a horizon in weeks/sprints ("how much?").
- Historical signal (optional but decisive): per-period throughput (items finished per week or sprint, oldest first), or ≥ 3 comparable past efforts with their actual durations. Read it from the tracker or the user; never invent history.
- Confidence level the audience needs (optional, default 85%).

## Procedure

1. **Pick the method by the data present — this choice is a rule, not a preference:**
   - ≥ 6 periods of throughput → *throughput Monte Carlo* (step 2).
   - else ≥ 3 comparable past efforts → *reference class* (step 3).
   - else → *cone of uncertainty* (step 4), and name the data that would upgrade it.
2. **Monte Carlo — run the bundled script, never simulate in prose:**

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/forecast/scripts/monte-carlo.py" \
     --throughput 3,5,2,4,6,0,4,5 --items 40          # "when are 40 items done?"
   # or: --periods 10                                   # "how many items in 10 weeks?"
   ```

   It is seeded (default 42), so the same history gives the same percentiles. Quote the percentile matching the audience's confidence (P85 by default) and paste the block verbatim. Exit 2 = bad history; fix the input.
3. **Reference class** — list the comparable efforts and their actual outcomes; the base rate is their median and range. Adjust only for named differences, each with a direction, size, and reason.
4. **Cone of uncertainty** — give an explicitly wide range (early-stage: 0.25×–4× of the best guess) labelled as a cone, plus what would narrow it.
5. **Name the assumptions that move the date most** (scope stability, staffing, unplanned work share) and the sensitivity of each.
6. **Re-forecast trigger** — the change (scope growth %, throughput drop) that should trigger a new run.

## Output

```text
Forecast: checkout v2 (40 items)        method: throughput Monte Carlo

Forecast (throughput Monte Carlo)
History:  8 weeks, items/week = 3,5,2,4,6,0,4,5  (median 4, mean 3.6)
Trials:   10000  seed 42
Question: when are 40 items done?

Result:
  P50  done within 11 weeks
  P70  done within 12 weeks
  P85  done within 13 weeks
  P95  done within 15 weeks

Answer (85% confidence): done within 13 weeks of the history's end.
Most date-moving assumption: scope stays at 40 items — each +10% scope adds ~1 week at this throughput.
Re-forecast trigger: scope grows > 20%, or 3-week rolling throughput drops below 3 items/week.
```

For reference class or cone, keep the header, `Answer`, assumption, and trigger lines; replace the script block with the base-rate table (effort, actual duration) or the cone bounds.

## Quality bar

- The answer is a range with an explicit confidence level, never a bare single date.
- Monte Carlo numbers come from the script run, pasted verbatim; nothing is "simulated" in prose.
- The method follows the data rule in step 1; pure gut is labelled a cone, not a forecast.
- Assumptions and their sensitivity are stated; the most date-moving one is named.
- Avoids re-deriving per-item three-point estimates — consumes `estimate` output if needed.
