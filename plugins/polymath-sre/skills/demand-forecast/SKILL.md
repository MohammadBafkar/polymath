---
name: demand-forecast
description: Model capacity demand — growth (linear/compound/seasonal), translate to resource needs + headroom, and flag the lead time before a saturation breach.
---

# demand-forecast

> Capacity planning fails on lead time, not math: you saw the trend but couldn't provision before the wall. Forecast far enough ahead to act, and state the date you run out.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Projecting whether current capacity survives expected growth or a known event (launch, sale, season).
- Turning a usage trend into a provisioning decision with a deadline.
- A workflow invokes `polymath-sre:demand-forecast`.

Not this when: you are setting reliability targets (`polymath-sre:slo-design`) or turning the forecast into scaling triggers and a cost plan (`polymath-sre:capacity-plan`, which consumes this output). This skill projects demand forward in time.

## Inputs

- Historical usage of the driving metric(s) (RPS, storage, connections), and the resource each consumes.
- Known future events and their expected multiplier; the provisioning lead time.

## Procedure

1. **Pick the driver metric(s)** that actually gate capacity (often RPS, concurrent users, data volume, queue depth) — forecast the driver, then map to resources, not the other way around.
2. **Choose a growth model from the data**: linear (steady adds), compound/exponential (% growth — the one teams underestimate), or seasonal/cyclical (day-of-week, holidays, campaigns). Fit with the bundled script — it compares linear vs compound by R² and never assumes linear because it's easy (seasonality: fit on de-seasonalized or same-period-last-year data, and say so):

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/capacity-plan/scripts/headroom.py" \
     --history <per-period values, oldest first> --period month \
     --capacity <max> --ceiling 0.7 --lead-time-days <n> --as-of <YYYY-MM-DD> [--event DATE:MULT]
   ```
3. **Overlay known events**: launches, marketing, seasonal peaks — apply explicit multipliers on top of the baseline trend.
4. **Translate demand → resources**: use the measured resource-per-unit (from `capacity-plan` / load tests) to convert forecasted driver units into CPU/memory/storage/instances. State the conversion.
5. **Apply a headroom target**: provision to a utilization ceiling (e.g. 60–70% at peak) so you have burst room and time to react — not 100%.
6. **Lead-time-to-breach**: the script's `Must act by:` line — the trend (or event) breach minus provisioning lead time. This is the output that matters; quote it, don't recompute it.
7. **State assumptions + confidence + refresh cadence**: forecasts decay — say when to re-run and what would invalidate it (a step-change in growth).

## Output

`docs/capacity/<slug>-forecast.md`, in this shape:

```text
Demand forecast: refund-service — requests/s at peak

Driver:      peak RPS (gates DB connections at 1.6 conns/RPS, measured in load test 2026-09)
Script:      <the headroom.py block, verbatim>
Resources:   peak 320 RPS → 512 conns; ceiling 700 conns ≈ 437 RPS
Headroom:    provision to ≤ 70% at peak
Must act by: 2027-04-18   confidence: medium (6 months of history, no seasonality yet)
Assumptions: growth stays compound ~4.5%/month; Black Friday ×1.3 (last year's ratio)
Refresh:     monthly, or immediately on a step change > 20% month-over-month
```

## Quality bar

- The growth model is fit to history, not assumed linear; compounding is checked.
- Demand is converted to resources via a measured per-unit cost, with headroom.
- The output names a concrete must-act-by date accounting for provisioning lead time.
- Assumptions, confidence, and a refresh cadence are stated.
