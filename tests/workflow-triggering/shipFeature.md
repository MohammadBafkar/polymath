---
workflow: shipFeature
trigger_prompts:
  - "ship this feature"
  - "build and ship this end to end"
  - "take this from PRD to PR"
  - "implement this small feature properly"
must_propose:
  - shipFeature
allow_propose:
  - featureFromIdea
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `shipFeature` workflow via the detect → propose contract (run-workflow/SKILL.md).
