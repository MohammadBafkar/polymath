---
workflow: reviewPlan
trigger_prompts:
  - "review this plan"
  - "is this plan any good before I start"
  - "poke holes in this plan"
  - "what's wrong with my design doc"
must_propose:
  - reviewPlan
allow_propose:
  - deliberationLoop
  - reviewPR
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `reviewPlan` workflow via the detect → propose contract (run-workflow/SKILL.md).
