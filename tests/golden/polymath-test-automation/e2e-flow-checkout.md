---
plugin: polymath-test-automation
scenario: e2e-checkout-journey
expect:
  invoked:
    - polymath-test-automation:e2e-flow
  output_matches:
    - "selector"
    - "wait"
  not_invoked:
    - polymath-qa:unit-tests
    - polymath-test-automation:load-test
timeout_seconds: 90
---

# Prompt

> Write an end-to-end browser test for the checkout journey: add to cart,
> enter shipping, pay, see confirmation.

Use polymath-test-automation:e2e-flow.

# Acceptance

- One spec covering the journey with role/test-id selectors and state-based (web-first) waits, no sleeps.
- Deterministic data seeding described; trace/screenshot on failure.
