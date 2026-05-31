---
plugin: polymath-qa
skill: test-smell
trigger_prompts:
  - "why is our test suite so flaky and slow"
  - "review these tests for anti-patterns"
  - "this test mocks everything and breaks on every change — what's wrong with it"
must_invoke:
  - polymath-qa:test-smell
allow_invoke:
  - polymath-qa:*
  - polymath-engineering:*
  - polymath-core:*
forbidden_prompts:
  - "write unit tests for this function"
  - "what tests is this diff missing"
---

# Why this test exists

Flaky/slow/brittle-suite phrasings are the canonical triggers. The
forbidden prompts guard the boundary against `unit-tests` (authoring) and
`coverage-gap` (missing coverage).
