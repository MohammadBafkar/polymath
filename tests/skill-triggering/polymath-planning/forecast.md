---
plugin: polymath-planning
skill: forecast
trigger_prompts:
  - "when will this realistically be done — give me a confidence range not a date"
  - "forecast the delivery date from our historical throughput"
  - "what's the probability we finish the backlog by end of quarter"
must_invoke:
  - polymath-planning:forecast
allow_invoke:
  - polymath-planning:*
  - polymath-core:*
forbidden_prompts:
  - "give a three-point estimate for this one task"
  - "break this initiative into work items"
---

# Why this test exists

Probabilistic / range / "when will it be done" forecasting routes here.
Forbidden prompts guard against `polymath-planning:estimate` (per-item
three-point) and `polymath-planning:work-breakdown` (decomposition).
