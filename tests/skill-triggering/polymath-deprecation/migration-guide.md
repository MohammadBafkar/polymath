---
plugin: polymath-deprecation
skill: migration-guide
trigger_prompts:
  - "write a migration guide for consumers moving off the v1 API"
  - "our customers need upgrade steps with before/after code"
  - "document how to move from the old config format to the new one"
must_invoke:
  - polymath-deprecation:migration-guide
allow_invoke:
  - polymath-deprecation:*
  - polymath-core:*
forbidden_prompts:
  - "plan the deprecation timeline with warn and remove dates"
  - "upgrade our codebase to the new dotnet version"
---

# Why this test exists

Consumer-upgrade-guide phrasings route here. Forbidden prompts guard against
the sibling `deprecation-plan` and the `migrateLanguageVersion` workflow.
