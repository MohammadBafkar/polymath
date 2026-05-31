---
plugin: polymath-product
skill: roadmap
trigger_prompts:
  - "lay out our roadmap for this quarter and beyond"
  - "I need a Now/Next/Later view to show stakeholders"
  - "turn this ranked list into a roadmap grouped by outcome"
must_invoke:
  - polymath-product:roadmap
allow_invoke:
  - polymath-product:*
  - polymath-prioritize:*
  - polymath-core:*
forbidden_prompts:
  - "rank these features by RICE"
  - "write a plan for building the rate limiter"
---

# Why this test exists

Roadmap / Now-Next-Later / horizon phrasings route here. Forbidden
prompts guard against `polymath-prioritize:prioritize` (ranking) and
`polymath-planning:write-plan` (change plan).
