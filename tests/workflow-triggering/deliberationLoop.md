---
workflow: deliberationLoop
trigger_prompts:
  - "pressure-test my approach"
  - "red-team my idea before I commit"
  - "critique this and give me a better plan"
  - "stress-test this and revise it"
must_propose:
  - deliberationLoop
allow_propose:
  - reviewPlan
  - decideUnderAmbiguity
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `deliberationLoop` workflow via the detect → propose contract (run-workflow/SKILL.md).
