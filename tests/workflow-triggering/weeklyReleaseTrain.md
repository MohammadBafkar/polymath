---
workflow: weeklyReleaseTrain
trigger_prompts:
  - "cut this week's release"
  - "prep the release train"
  - "draft release notes for this version"
  - "do the weekly release"
must_propose:
  - weeklyReleaseTrain
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `weeklyReleaseTrain` workflow via the detect → propose contract (run-workflow/SKILL.md).
