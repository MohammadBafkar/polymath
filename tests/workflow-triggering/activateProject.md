---
workflow: activateProject
trigger_prompts:
  - "set up polymath for this repo"
  - "onboard this project"
  - "initialize project context"
  - "generate onboarding docs"
must_propose:
  - activateProject
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `activateProject` workflow via the detect → propose contract (run-workflow/SKILL.md).
