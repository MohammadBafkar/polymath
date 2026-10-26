---
name: capacity-plan
description: Turn a demand projection into a capacity plan — constrained resource, headroom date, scaling triggers, and cost; not forecasting the demand itself (demand-forecast).
---

# capacity-plan

> A headroom plan, not a point-in-time reading. It projects demand forward and
> names the trigger at which you must act — before the SLO burns, not after.

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
3. **Headroom.** Compute when projected demand crosses the safe-utilization
   threshold (leave margin below 100% for spikes and failover). Report the date
   or event, not just a percentage.
4. **Scaling triggers.** Define the leading-indicator threshold that fires action
   *before* the SLO is at risk (e.g. "scale out at 70% sustained for 10m"). Tie it
   to the SLO's error budget.
5. **Cost.** State the cost of the added capacity and of *not* adding it (SLO breach,
   incident). Name the cheaper-to-reverse option when growth is uncertain.

## Output

- File: `docs/capacity/<slug>.md` — baseline, growth model + assumption,
  headroom date/event, scaling triggers, and cost trade-off.
- One-line summary: the constrained dimension and the date/event headroom runs out.

## Quality bar

- The growth model's assumption is explicit and evidence-backed, not implied.
- Headroom is expressed as a date or event, not a bare percentage.
- The scaling trigger fires before the SLO is at risk, with margin for failover.
- Cost names both adding and not-adding capacity.
