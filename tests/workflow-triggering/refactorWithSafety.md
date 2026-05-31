---
workflow: refactorWithSafety
trigger_prompts:
  - "refactor this safely"
  - "clean up this module without breaking it"
  - "restructure this code with a safety net"
  - "pin behavior then refactor"
must_propose:
  - refactorWithSafety
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `refactorWithSafety` workflow via the detect → propose contract (run-workflow/SKILL.md).
