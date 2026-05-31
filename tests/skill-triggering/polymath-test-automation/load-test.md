---
plugin: polymath-test-automation
skill: load-test
trigger_prompts:
  - "load test the checkout API at expected peak traffic"
  - "I need a k6 script to find our breaking point under stress"
  - "will the service hold at 2k requests per second"
must_invoke:
  - polymath-test-automation:load-test
allow_invoke:
  - polymath-test-automation:*
  - polymath-performance:*
  - polymath-core:*
forbidden_prompts:
  - "set a performance budget for this endpoint"
  - "write a browser test for the checkout journey"
---

# Why this test exists

Load/stress/k6/throughput phrasings route here. Forbidden prompts guard
against `polymath-performance:perf-budget` (setting targets) and the
sibling `e2e-flow`.
