---
plugin: polymath-product
scenario: product-strategy-new-segment
expect:
  invoked:
    - polymath-product:product-strategy
  output_matches:
    - "ICP"
    - "positioning"
  not_invoked:
    - polymath-product:prd
timeout_seconds: 90
---

# Prompt

> We're thinking of moving upmarket to mid-market teams. Help me think
> through the strategy — who exactly, how we position, how we price.

Use polymath-product:product-strategy.

# Acceptance

- ICP names who it's for AND who it's not; positioning names the competitive alternative.
- Pricing/packaging with a value metric; moat explains why the advantage compounds.
- Key bets stated as assumptions with a cheap test; success leading indicator named.
