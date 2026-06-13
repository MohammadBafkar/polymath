---
workflow: techDebtPaydown
trigger_prompts:
  - "pay down our tech debt"
  - "find and address our technical debt"
  - "tackle the tech debt in this area"
  - "make a technical-debt paydown plan and start it"
must_propose:
  - techDebtPaydown
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `techDebtPaydown` workflow via the detect → propose contract (run-workflow/SKILL.md). It identifies + quantifies debt, plans the paydown, then addresses the top item behind a test safety net.
