---
workflow: deprecationToRemoval
trigger_prompts:
  - "deprecate this over time"
  - "plan a multi-quarter sunset"
  - "kill this API once usage drops"
  - "retire this feature on a schedule"
must_propose:
  - deprecationToRemoval
allow_propose:
  - sunsetCapability
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `deprecationToRemoval` workflow via the detect → propose contract (run-workflow/SKILL.md).
