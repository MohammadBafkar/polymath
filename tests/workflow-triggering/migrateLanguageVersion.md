---
workflow: migrateLanguageVersion
trigger_prompts:
  - "upgrade us to the new runtime version"
  - "migrate to the new language version"
  - "bump the language version across the repo"
  - "do a phased runtime migration"
must_propose:
  - migrateLanguageVersion
allow_propose:
  - bumpDependency
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `migrateLanguageVersion` workflow via the detect → propose contract (run-workflow/SKILL.md).
