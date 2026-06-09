---
plugin: polymath-cloud
skill: cloud-cost-review
trigger_prompts:
  - "our cloud bill is rising and I don't know why — help me cut it"
  - "review our AWS spend for waste and rightsizing"
  - "what's our cost per request and how do we bring it down"
must_invoke:
  - polymath-cloud:cloud-cost-review
allow_invoke:
  - polymath-cloud:*
  - polymath-cloud:*
  - polymath-core:*
forbidden_prompts:
  - "report the always-on token cost of our plugins"
  - "plan capacity for next quarter's traffic"
---

# Why this test exists

Cloud-cost/FinOps phrasings route here. Forbidden prompts guard against
`polymath-core:plugin-budget` (internal token cost) and
`polymath-sre:capacity-plan` (capacity, not cost).
