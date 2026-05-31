---
plugin: polymath-qa
skill: assertion-quality
trigger_prompts:
  - "this test passes but I don't think it would catch the bug"
  - "our snapshot assertions break on every change and prove nothing"
  - "are these assertions actually checking the right behavior"
must_invoke:
  - polymath-qa:assertion-quality
allow_invoke:
  - polymath-qa:*
  - polymath-core:*
forbidden_prompts:
  - "write tests for this module"
  - "find the test smells across the whole suite"
---

# Why this test exists

Weak-assertion phrasings route here. Forbidden prompts guard against
`unit-tests` (authoring) and `test-smell` (suite-wide smell scan).
