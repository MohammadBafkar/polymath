---
workflow: respondToIncident
trigger_prompts:
  - "we have an incident"
  - "prod is down, help"
  - "page just fired, walk me through response"
  - "sev1, what do I do"
  - "take this incident from response all the way to action items"
must_propose:
  - respondToIncident
allow_propose:
  - bugTriage
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `respondToIncident` workflow via the detect → propose contract (run-workflow/SKILL.md).
