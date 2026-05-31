---
plugin: polymath-qa
skill: integration-contract
trigger_prompts:
  - "how do I test the boundary between our service and the payments API"
  - "set up contract tests so the provider can't break us"
  - "what should I stub vs actually hit in these cross-service tests"
must_invoke:
  - polymath-qa:integration-contract
allow_invoke:
  - polymath-qa:*
  - polymath-core:*
forbidden_prompts:
  - "write a unit test for this pure function"
  - "what's our overall testing strategy"
---

# Why this test exists

Boundary / contract / stub-vs-hit phrasings route here. Forbidden prompts
guard against `unit-tests` and `test-strategy`.
