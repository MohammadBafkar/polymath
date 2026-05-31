---
workflow: reviewPR
trigger_prompts:
  - "review this PR"
  - "do a thorough review of my diff"
  - "run all the critics on this change"
  - "review the working tree before I push"
must_propose:
  - reviewPR
allow_propose:
  - reviewPlan
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `reviewPR` workflow via the detect → propose contract (run-workflow/SKILL.md).
