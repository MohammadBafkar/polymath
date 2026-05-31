---
workflow: perfRegression
trigger_prompts:
  - "latency went up, find out why"
  - "p99 regressed after the last deploy"
  - "this got slow, fix it"
  - "throughput dropped, investigate and fix"
must_propose:
  - perfRegression
allow_propose:
  - rootCauseAnalysis
  - bugTriage
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `perfRegression` workflow via the detect → propose contract (run-workflow/SKILL.md).
