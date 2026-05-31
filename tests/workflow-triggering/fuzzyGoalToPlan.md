---
workflow: fuzzyGoalToPlan
trigger_prompts:
  - "I have a fuzzy goal, help me plan it"
  - "turn this vague idea into a plan"
  - "story-map and estimate this"
  - "help me scope and estimate this work"
must_propose:
  - fuzzyGoalToPlan
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `fuzzyGoalToPlan` workflow via the detect → propose contract (run-workflow/SKILL.md).
