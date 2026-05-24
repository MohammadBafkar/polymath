---
plugin: polymath-connector-stripe
scenario: triage-dispute
expect:
  invoked:
    - polymath-connector-stripe:refund-or-dispute-triage
  output_matches:
    - "(dp_|charge|dispute)"
    - "(events.list|lifecycle|timeline)"
    - "(operator|approval|proposed)"
timeout_seconds: 90
---

# Prompt

> Triage Stripe dispute dp_1OefGH. The customer says they were
> charged twice for order ord_12345.

Use polymath-connector-stripe:refund-or-dispute-triage.

# Acceptance

- Object kind resolved from the dp_ prefix.
- Lifecycle replayed via events.list.
- Proposed action surfaced as an explicit API call, not auto-executed.
- Customer-safe summary contains no PAN/BIN/anti-fraud signal.
