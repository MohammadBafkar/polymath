---
plugin: polymath-progressive-delivery
skill: safe-rollout
trigger_prompts:
  - "how do we roll this out behind a flag without taking everyone down at once"
  - "design a canary rollout with automatic rollback if errors spike"
  - "we need to ship this risky change gradually with a way to bail"
must_invoke:
  - polymath-progressive-delivery:safe-rollout
allow_invoke:
  - polymath-sre:*
  - polymath-devops:*
  - polymath-core:*
forbidden_prompts:
  - "promote this build from staging to production"
  - "design an A/B test to measure conversion"
---

# Why this test exists

Flag/canary/gradual-rollout phrasings route here. Forbidden prompts guard
the boundary against `polymath-devops:env-promotion` (build→env) and
`polymath-data:run-experiment` (A/B to learn).
