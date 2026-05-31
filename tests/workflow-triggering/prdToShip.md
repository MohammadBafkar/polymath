---
workflow: prdToShip
trigger_prompts:
  - "we already have a PRD, build and ship it"
  - "implement this existing spec end to end"
  - "take this PRD to a PR"
  - "build from the spec we already wrote"
must_propose:
  - prdToShip
allow_propose:
  - shipFeature
  - featureFromIdea
forbidden_prompts:
  - "format my markdown"
---

Naive prompts that must surface the `prdToShip` workflow (ship from an existing PRD, skipping the prd step).
