---
workflow: featureFromIdea
trigger_prompts:
  - "do discovery then ship this"
  - "interview users then build it"
  - "take this from research to PR"
  - "validate this idea then build it"
must_propose:
  - featureFromIdea
allow_propose:
  - shipFeature
  - experimentToGA
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `featureFromIdea` workflow via the detect → propose contract (run-workflow/SKILL.md).
