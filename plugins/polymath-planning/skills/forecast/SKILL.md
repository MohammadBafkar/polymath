---
name: forecast
description: Forecast a delivery date/scope as a probability range — reference-class, throughput/Monte-Carlo, cone of uncertainty. Range forecasting from data, not per-item estimation (estimate).
---

# forecast

> "When will it be done?" deserves a probability, not a date. Forecast from how work has actually flowed, and quote a range with a confidence.

## When to use

- A delivery date / scope-by-date needs a defensible probabilistic answer, ideally from historical data.
- Someone is being pressured into a single-date commitment for multi-item work.
- A workflow invokes `polymath-planning:forecast`.

This forecasts *aggregate delivery under uncertainty*. It is not per-item three-point sizing (`polymath-planning:estimate`), task breakdown (`polymath-planning:work-breakdown`), or capacity planning (`polymath-sre:capacity-plan`).

## Inputs

- The scope (item count / backlog) or the date being forecast.
- Historical signal if available: past throughput (items/week), cycle times, or analogous past projects.
- The confidence level the audience needs (e.g. 85%).

## Procedure

1. **Pick the method** by the data you have:
   - *Reference-class* — find ≥3 comparable past efforts; use their actual outcomes as the base rate, then adjust. Beats bottom-up when history exists.
   - *Throughput / Monte-Carlo* — sample historical weekly throughput (or cycle time) to simulate completion; report the distribution.
   - *Cone of uncertainty* — when little data exists, give an explicitly wide range and say what would narrow it.
2. **Quote a range, not a point** — e.g. "85% confidence: done by week 9–12", with the confidence level stated.
3. **State the base rate and adjustments** — what historical data anchored the forecast, and every adjustment you made (with reasoning).
4. **Name the assumptions** that most move the forecast (scope stability, staffing, no big unknowns) and how sensitive the date is to each.
5. **Re-forecast trigger** — what change (scope creep %, throughput drop) should trigger an update.

## Quality bar

- The answer is a range with an explicit confidence level, never a bare single date.
- It is anchored to historical data (reference class or throughput) when any exists; pure gut is flagged as such.
- Assumptions and their sensitivity are stated; the most date-moving one is named.
- Avoids re-deriving per-item three-point estimates — consumes `estimate` output if needed.
