---
workflow: capacityReview
trigger_prompts:
  - "do a capacity review"
  - "will we run out of capacity before"
  - "forecast and plan our capacity"
  - "capacity plan for the upcoming growth"
must_propose:
  - capacityReview
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `capacityReview` workflow via the detect → propose contract (run-workflow/SKILL.md). It forecasts demand forward, sizes resources with headroom, then writes the provisioning plan with a must-act-by date.
