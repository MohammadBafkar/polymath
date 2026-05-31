---
plugin: polymath-test-automation
skill: e2e-flow
trigger_prompts:
  - "write a Playwright test for the signup flow"
  - "I need a browser end-to-end test for checkout"
  - "automate clicking through the core user journey in the UI"
must_invoke:
  - polymath-test-automation:e2e-flow
allow_invoke:
  - polymath-test-automation:*
  - polymath-qa:*
  - polymath-core:*
forbidden_prompts:
  - "write a unit test for this function"
  - "load test the search API at 2k rps"
---

# Why this test exists

Browser/e2e/Playwright/journey phrasings route here. Forbidden prompts
guard against `polymath-qa:unit-tests` and the sibling `load-test`.
