---
workflow: bugTriage
trigger_prompts:
  - "help me triage this bug"
  - "figure out why this is broken"
  - "investigate this defect and plan the fix"
  - "there's a bug, where do I start"
must_propose:
  - bugTriage
allow_propose:
  - rootCauseAnalysis
  - perfRegression
  - respondToIncident
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `bugTriage` workflow via the detect → propose contract (run-workflow/SKILL.md).
