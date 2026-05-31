---
workflow: progressiveRollout
trigger_prompts:
  - "roll this out behind a flag in stages with guardrails"
  - "progressively release this without an A/B test"
  - "ramp this feature from 1% to 100% safely"
  - "flag rollout with SLO health gates and rollback"
must_propose:
  - progressiveRollout
allow_propose:
  - experimentToGA
  - shipFeature
forbidden_prompts:
  - "format my markdown"
---

Naive prompts that must surface the `progressiveRollout` workflow (staged flag rollout with SLO gates, no A/B).
