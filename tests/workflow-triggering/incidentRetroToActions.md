---
workflow: incidentRetroToActions
trigger_prompts:
  - "turn this postmortem into tickets"
  - "file action items from the retro"
  - "track the follow-ups from this incident"
  - "make tickets from this postmortem"
must_propose:
  - incidentRetroToActions
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `incidentRetroToActions` workflow via the detect → propose contract (run-workflow/SKILL.md).
