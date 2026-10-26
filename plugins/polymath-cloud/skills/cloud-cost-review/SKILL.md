---
name: cloud-cost-review
description: Review cloud spend — rightsizing/waste, cost budgets + anomaly alerts, unit economics (cost per request/tenant), reserved coverage. Cloud cost, not internal token budgets (plugin-budget).
---

# cloud-cost-review

> Cloud cost is an engineering signal, not a finance afterthought. Tie spend to units served, kill waste, and make the bill attributable.

## When to use

- A cloud bill is rising, surprising, or unattributed, and you need where-the-money-goes plus actions.
- The user asks about FinOps, rightsizing, savings plans, cost per request/tenant, or a cost budget/anomaly alert.
- A workflow invokes `polymath-cloud:cloud-cost-review`.

This is *cloud* cost. It is not Polymath's internal listing token budget (`polymath-core:plugin-budget`, `polymath-author:token-budget-report`), capacity/scaling (`polymath-sre:capacity-plan`), or picking an architecture (`polymath-cloud:design-aws-pattern` / `design-azure-pattern` / `design-gcp-pattern` — though it consumes their cost dimension).

## Inputs

- Cost data: bill by service/SKU/account, ideally tagged; or the architecture if no data yet.
- The unit that matters (request, tenant, job, GB) for unit economics.
- Commitment posture (on-demand vs reserved/savings plans) and risk tolerance.

## Procedure

1. **Attribute** — break spend by service/SKU and by owner/team via tags; flag untagged spend (the attribution gap).
2. **Waste** — find idle/oversized resources, orphaned volumes/IPs, old snapshots, over-provisioned instances, dev left running; quantify each.
3. **Rightsize** — recommend instance/SKU/tier changes from utilization, with the expected saving and the risk.
4. **Unit economics** — compute cost per chosen unit; trend it. Rising cost/unit is the real alarm, not absolute spend growth that tracks usage.
5. **Commitments** — assess reserved/savings-plan coverage vs steady-state baseline; recommend coverage %, not 100%.
6. **Guardrails** — propose a cost budget and an anomaly alert (threshold or ML) so the next surprise pages someone.
7. Never delete or resize anything yourself — recommendations only; the owner acts.

## Output

```text
Cloud cost review: <account/project>, <period>

Attributed spend:   $48.2k/mo — compute 52%, storage 21%, data transfer 14%, other 13%
Untagged:           $6.1k/mo (12.7%) — owners unknown
Unit economics:     $0.0031 per refund (↑ 18% QoQ while volume ↑ 4%)  ← the real alarm

Actions (ranked by $ saved):
  1. Delete 41 unattached volumes + 2.3 TB old snapshots   ~$2.4k/mo   risk: low (verify no restore need)
  2. Rightsize 12 m5.2xlarge at < 15% CPU → m5.large        ~$3.1k/mo   risk: medium (check memory headroom)
  3. Savings Plan covering 60% of steady-state compute      ~$4.0k/mo   risk: 1-yr commitment

Guardrails:  monthly budget $50k (alert at 80%/100%); anomaly alert on daily spend > 25% vs 7-day mean
```

## Quality bar

- Spend is attributed; untagged/unattributed spend is quantified, not ignored.
- Every recommendation carries an estimated $ saving and its risk.
- Unit economics (cost per request/tenant) is computed, not just total spend.
- A budget + anomaly alert is proposed so cost regressions are caught automatically.
