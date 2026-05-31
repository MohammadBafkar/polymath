---
workflow: securityFinding
trigger_prompts:
  - "fix this security finding"
  - "we have a vuln, patch it"
  - "address this OWASP issue"
  - "remediate this security report"
must_propose:
  - securityFinding
allow_propose:
  - bumpDependency
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `securityFinding` workflow via the detect → propose contract (run-workflow/SKILL.md).
