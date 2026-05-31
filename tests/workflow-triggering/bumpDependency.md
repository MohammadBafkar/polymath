---
workflow: bumpDependency
trigger_prompts:
  - "bump this dependency to the latest"
  - "upgrade this package safely"
  - "is it safe to bump this library"
  - "patch this CVE in a dependency"
must_propose:
  - bumpDependency
allow_propose:
  - migrateLanguageVersion
  - securityFinding
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `bumpDependency` workflow via the detect → propose contract (run-workflow/SKILL.md).
