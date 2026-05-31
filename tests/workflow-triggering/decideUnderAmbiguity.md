---
workflow: decideUnderAmbiguity
trigger_prompts:
  - "help me decide between these options"
  - "we need to make a call on this"
  - "should we do A or B"
  - "run a DACI and record the decision"
must_propose:
  - decideUnderAmbiguity
allow_propose:
  - deliberationLoop
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `decideUnderAmbiguity` workflow via the detect → propose contract (run-workflow/SKILL.md).
