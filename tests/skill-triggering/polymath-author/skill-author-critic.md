---
plugin: polymath-author
skill: skill-author-critic
trigger_prompts:
  - "review my draft SKILL.md and tell me ACCEPT / REVISE / REWRITE"
  - "is this skill description specific enough to trigger reliably?"
  - "audit my plugin's SKILL.md against the style guide and name the anti-patterns"
must_invoke:
  - polymath-author:skill-author-critic
allow_invoke:
  - polymath-author:*
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

A meta-test: the catalog's own skill that critiques other SKILL.md
files must itself trigger on plausible plugin-author prompts.
