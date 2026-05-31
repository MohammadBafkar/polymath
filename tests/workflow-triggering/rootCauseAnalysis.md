---
workflow: rootCauseAnalysis
trigger_prompts:
  - "do a root cause analysis"
  - "why did this really happen"
  - "run a 5-whys on this"
  - "write an RCA for this symptom"
must_propose:
  - rootCauseAnalysis
allow_propose:
  - bugTriage
  - perfRegression
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `rootCauseAnalysis` workflow via the detect → propose contract (run-workflow/SKILL.md).
