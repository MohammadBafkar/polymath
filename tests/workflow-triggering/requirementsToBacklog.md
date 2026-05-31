---
workflow: requirementsToBacklog
trigger_prompts:
  - "turn this PRD into a backlog"
  - "break this requirements doc into ready stories"
  - "decompose and groom this spec into work items"
  - "go from PRD to a sprint-ready backlog"
must_propose:
  - requirementsToBacklog
allow_propose:
  - prdToShip
  - featureFromIdea
forbidden_prompts:
  - "format my markdown"
---

Naive prompts that must surface the `requirementsToBacklog` workflow (PRD → decomposed, groomed, estimated backlog).
