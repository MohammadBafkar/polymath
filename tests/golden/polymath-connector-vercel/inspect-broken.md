---
plugin: polymath-connector-vercel
scenario: inspect-broken
expect:
  invoked:
    - polymath-connector-vercel:inspect-deployment
  output_matches:
    - "(dpl_|deployment)"
    - "(5xx|runtime|edge)"
    - "(rollback|promote|previous)"
timeout_seconds: 90
---

# Prompt

> Inspect production deployment dpl_abcDEF. Customers report 502s on
> refund routes since 14:02.

Use polymath-connector-vercel:inspect-deployment.

# Acceptance

- State + build + runtime + edge evidence each surfaced.
- Classification is one of healthy / degraded / broken with named thresholds.
- Rollback target is the previous READY *production* deployment, not just the previous one.
- Promote is surfaced as a proposed operator action, not auto-executed.
