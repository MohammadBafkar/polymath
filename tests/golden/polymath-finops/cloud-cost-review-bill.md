---
plugin: polymath-finops
scenario: rising-aws-bill
expect:
  invoked:
    - polymath-finops:cloud-cost-review
  output_matches:
    - "rightsizing"
    - "unit"
  not_invoked:
    - polymath-core:plugin-budget
    - polymath-sre:capacity-plan
timeout_seconds: 90
---

# Prompt

> Our AWS bill jumped 40% last month and nobody knows why. Find where the
> money's going and what we should do about it.

Use polymath-finops:cloud-cost-review.

# Acceptance

- Spend attributed by service/owner; untagged spend quantified.
- Ranked waste/rightsizing actions each with an estimated $ saving.
- Unit economics (cost per request/tenant) computed; a budget + anomaly alert proposed.
