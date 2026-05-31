---
workflow: incidentToReview
trigger_prompts:
  - "take this incident from response all the way to action items"
  - "respond to this incident and then track the follow-ups"
  - "handle the outage and produce the postmortem actions"
  - "incident response through to retro work items"
must_propose:
  - incidentToReview
allow_propose:
  - respondToIncident
  - incidentRetroToActions
forbidden_prompts:
  - "format my markdown"
---

Naive prompts that must surface the `incidentToReview` workflow (live incident → filed follow-up actions).
