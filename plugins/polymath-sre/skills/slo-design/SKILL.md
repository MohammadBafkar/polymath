---
name: slo-design
description: Design an SLO — pick the right SLI per critical user journey, set the threshold by the 28-day error-budget arithmetic, document the measurement.
---

# slo-design

> Design one SLO per critical user journey. Output is the SLI, threshold, measurement window, and the burn-rate alert structure.

## When to use

- A new service is going live and needs an SLO before opening real traffic.
- An existing service has alerts but no SLO; on-call is firefighting symptoms not promises.

## Procedure

1. **Identify the critical user journey** (CUJ). Not the service — the journey. "User opens checkout, sees totals within 1s" is a CUJ; "API responds with 200" is not.
2. **Pick the SLI** for that journey. Two flavors usually suffice:
   - **Availability SLI**: `successful_requests / total_requests` within the journey.
   - **Latency SLI**: `requests_under_X_ms / total_requests` within the journey.
   "Success" must be defined precisely — does 5xx count as failure? Does 429? Does a 200 with empty body count as success? Document.
3. **Pick the threshold**:
   - Availability: 99.0%, 99.5%, 99.9%, 99.95% — based on what the journey actually needs. Don't reach for 99.99% reflexively; the budget gets too tight to ship anything.
   - Latency: pick a single percentile (P95 or P99) and a single threshold. Avoid "P50 < 100ms AND P99 < 500ms" pyramids.
4. **Measurement window** — 28 days rolling is the default. Long enough to absorb a bad day; short enough to be actionable.
5. **Error budget arithmetic** (28 days = 40,320 minutes; budget = (1 − SLO) × window):
   - 99.0% = 6h 43m 12s per 28d.
   - 99.5% = 3h 21m 36s per 28d.
   - 99.9% = 40m 19s per 28d.
   - 99.95% = 20m 10s per 28d.
   - 99.99% = 4m 2s per 28d — almost certainly too tight.
   (The familiar 43m 12s / 21m 36s / 4m 19s figures are for a 30-day window — don't mix them with 28d.)
6. **Burn-rate alerts** — Google SRE workbook's multi-window, multi-burn-rate shape. Each alert fires only when **both** its long and short window exceed the rate (the short window makes it reset quickly once the burn stops):

   | Long window | Short window | Budget consumed | Burn rate (30d / 28d) | Severity |
   | ----------- | ------------ | --------------- | --------------------- | -------- |
   | 1h          | 5m           | 2%              | 14.4× / 13.44×        | page |
   | 6h          | 30m          | 5%              | 6× / 5.6×             | page |
   | 3d          | 6h           | 10%             | 1× / 0.93×            | ticket |

   burn rate = budget fraction × window hours ÷ long-window hours. Using the workbook's 30-day numbers on a 28-day SLO is fine if you say so; don't invent thresholds.

## Output

```text
SLO: refund-creation latency

Critical user journey:
  User triggers a refund from order details; refund record created in our DB.

SLI:
  fraction of POST /v1/orders/{id}/refunds requests returning 201 within 500ms,
  excluding 4xx (counted as success) and 5xx (counted as failure).

SLO:
  99.5% of refund-creation requests succeed within 500ms over a 28-day
  rolling window.

Error budget:
  0.5% × 40,320 min = 201.6 min = 3h 21m 36s per 28d.

Burn-rate alerts (28d rates):
  - 1h & 5m windows  @ 13.44× burn → page payments oncall
  - 6h & 30m windows @ 5.6× burn   → page payments oncall
  - 3d & 6h windows  @ 0.93× burn  → ticket to payments team

Where measured:
  Prometheus rule `slo_refund_latency_success_rate` (defined in
  monitoring/refund-slo.yaml).
```

## Anti-patterns to avoid

- One SLO covering "the whole service". Pick the journey.
- 99.99% for a service whose dependencies are 99.9%.
- Multi-percentile latency SLOs ("P50 AND P99 AND…").
- Alerting on every threshold dip; alert on burn rate.
