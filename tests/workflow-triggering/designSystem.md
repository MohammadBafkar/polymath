---
workflow: designSystem
trigger_prompts:
  - "design this system"
  - "write an architecture doc for this"
  - "how should I architect this"
  - "draft an RFC for this change"
must_propose:
  - designSystem
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `designSystem` workflow via the detect → propose contract (run-workflow/SKILL.md).
