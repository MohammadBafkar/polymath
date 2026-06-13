---
workflow: gameDay
trigger_prompts:
  - "run a game day"
  - "design a chaos experiment for"
  - "test our resilience with a controlled failure"
  - "game day for the failover"
must_propose:
  - gameDay
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `gameDay` workflow via the detect → propose contract (run-workflow/SKILL.md). It designs a chaos experiment with a hypothesis + abort, observes the live behavior, then captures findings as a blameless write-up with actions.
