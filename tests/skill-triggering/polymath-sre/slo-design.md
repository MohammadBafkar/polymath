---
plugin: polymath-sre
skill: slo-design
trigger_prompts:
  - "design an SLO for the refund API"
  - "we need an availability SLI/SLO for our auth service"
  - "pick the SLI per critical user journey and set thresholds with 28-day error-budget math"
must_invoke:
  - polymath-sre:slo-design
allow_invoke:
  - polymath-sre:error-budget-policy
  - polymath-observability:metrics-design
  - polymath-core:*
---

# Why this test exists

The third prompt is intentionally dense in SLO vocabulary (SLI,
critical user journey, error budget) to confirm the description
triggers on those phrases without the literal "SLO design".
