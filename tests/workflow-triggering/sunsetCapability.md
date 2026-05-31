---
workflow: sunsetCapability
trigger_prompts:
  - "sunset this endpoint"
  - "deprecate this with a customer notice"
  - "add deprecation warnings and a sunset notice"
  - "write the sunset notice and deprecate"
must_propose:
  - sunsetCapability
allow_propose:
  - deprecationToRemoval
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `sunsetCapability` workflow via the detect → propose contract (run-workflow/SKILL.md).
