---
workflow: estimateAndPlan
trigger_prompts:
  - "scope and estimate this, then write the plan"
  - "break this down, estimate it, and plan it"
  - "give me a WBS, estimate, and an executable plan"
  - "turn this clear goal into an estimated plan"
must_propose:
  - estimateAndPlan
allow_propose:
  - fuzzyGoalToPlan
forbidden_prompts:
  - "format my markdown"
---

Naive prompts that must surface the `estimateAndPlan` workflow (clear goal → WBS + estimate + plan).
