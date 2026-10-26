---
name: capacity-plan
description: Turn a demand projection into a capacity plan — constrained resource, headroom date, scaling triggers, and cost; not forecasting the demand itself (demand-forecast).
---

# capacity-plan

> A headroom plan, not a point-in-time reading. It projects demand forward and
> names the trigger at which you must act — before the SLO burns, not after.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A service is approaching a known growth event (launch, seasonal peak, new tenant).
- An SLO or error budget is trending toward exhaustion and you need runway.
- A workflow or review asks "will this scale, and when do we add capacity?".

## Inputs

- The service / resource and the constrained dimension (CPU, memory, connections, IOPS, QPS, storage).
- Current utilization and the historical growth signal if available.
- The SLO the capacity must protect (link `polymath-sre:slo-design` if undefined).

## Procedure

1. **Baseline.** State current utilization of the constrained dimension and the
   measurement window. Cite the metric (lean on `polymath-observability:metrics-design`
   for the RED/USE signal if it doesn't exist yet).
2. **Demand input.** Take the demand projection from `polymath-sre:demand-forecast`
   when one exists. Without one, use a simple stated model (linear / compounding /
   step) and label the growth rate as an assumption with its evidence — run
   `demand-forecast` when seasonality or known events matter.
3. **Headroom — run the bundled script, never project by hand.** It fits
   linear vs compound growth to the history (or takes a stated growth rate),
   finds when demand crosses the safe ceiling (margin below 100% for spikes and
   failover), overlays known events, and subtracts the provisioning lead time:

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/capacity-plan/scripts/headroom.py" \
     --history 410,430,445,460,490,512 --period month --capacity 1000 \
     --ceiling 0.7 --lead-time-days 42 --as-of 2026-10-26 --event 2026-11-27:1.3
   ```

   `--as-of` is the date of the last observation (it makes the dates
   reproducible). Report the date or event, not just a percentage.
4. **Scaling triggers.** Define the leading-indicator threshold that fires action
   *before* the SLO is at risk (e.g. "scale out at 70% sustained for 10m"). Tie it
   to the SLO's error budget.
5. **Cost.** State the cost of the added capacity and of *not* adding it (SLO breach,
   incident). Name the cheaper-to-reverse option when growth is uncertain.

## Output

`docs/capacity/<slug>.md` (slug = the service name, lowercased, non-`a-z0-9` runs → `-`), in this shape:

```markdown
# Capacity plan: refund-service — DB connections

Baseline: 512 of 1,000 pooled connections at p95 (28-day window, metric `pg_pool_in_use`).
Demand: from docs/capacity/refund-service-forecast.md (or: stated model — assumption, evidence: …).

Headroom forecast (as of 2026-10-26)
History:   6 months: 410,430,445,460,490,512  (oldest first)
Fit:       linear   +20.14/month    R² 0.986
           compound +4.49%/month    R² 0.991   ← chosen (higher R²)
Ceiling:   700 (70% of capacity 1000)
Now:       512 (73% of ceiling)
Trend:     breach in 7.1 months → 2027-05-30
Event:     2026-11-27 ×1.3 → projected 697.0  ok (99.6% of ceiling)
Lead time: 42 days
Must act by: 2027-04-18 (first breach 2027-05-30, trend)

Scaling trigger: pool in-use ≥ 65% for 10m → add a read replica (fires before the 70% ceiling).
Cost: +1 replica ≈ [TBD: monthly cost from billing] vs. not adding: Black Friday lands at 99.6% of ceiling — one failover from SLO breach.
```

One-line summary: the constrained dimension and the must-act-by date.

## Quality bar

- The growth model's assumption is explicit and evidence-backed, not implied.
- Headroom is expressed as a date or event, not a bare percentage.
- The scaling trigger fires before the SLO is at risk, with margin for failover.
- Cost names both adding and not-adding capacity.
