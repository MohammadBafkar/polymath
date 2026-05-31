---
workflow: experimentToGA
trigger_prompts:
  - "plan an A/B test to GA"
  - "pre-register an experiment then decide GA"
  - "stage a percentage rollout"
  - "should we GA this feature"
must_propose:
  - experimentToGA
allow_propose:
  - featureFromIdea
  - shipFeature
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `experimentToGA` workflow via the detect → propose contract (run-workflow/SKILL.md).
