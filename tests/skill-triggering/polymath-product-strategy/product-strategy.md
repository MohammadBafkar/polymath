---
plugin: polymath-product-strategy
skill: product-strategy
trigger_prompts:
  - "help me think through our product strategy for moving upmarket"
  - "how should we position and price this for a new segment"
  - "what's our go-to-market and where's the moat"
must_invoke:
  - polymath-product-strategy:product-strategy
allow_invoke:
  - polymath-product-strategy:*
  - polymath-product:*
  - polymath-research:*
  - polymath-core:*
forbidden_prompts:
  - "write a PRD for the new export feature"
  - "draft an exec brief recommending we hire two engineers"
---

# Why this test exists

Strategy/positioning/pricing/GTM/moat phrasings route here. Forbidden prompts
guard against `polymath-product:prd` (feature spec) and
`polymath-communication:exec-brief` (decision brief).
