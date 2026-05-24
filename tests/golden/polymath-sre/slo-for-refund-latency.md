---
plugin: polymath-sre
scenario: slo-for-refund-latency
expect:
  invoked:
    - polymath-sre:slo-design
  output_matches:
    - "SLI"
    - "(28-day|28 days|28d)"
    - "burn rate"
    - "(99\\.5|99\\.9)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Design an SLO for the refund-creation endpoint.

Use polymath-sre:slo-design. Critical user journey: user triggers
a refund from order details; refund record created in our DB.
P99 latency in prod is currently ~350ms. We page on PagerDuty.

# Acceptance

- One Critical User Journey named, not "the service".
- SLI definition specifies success criteria (status codes, latency
  threshold).
- SLO threshold is a single number (e.g. 99.5%) with a 28-day window.
- Burn-rate alerts use multiple windows (e.g. 1h/6h or similar
  multi-window pattern).
- Error-budget arithmetic explicit (X minutes per 28 days).
