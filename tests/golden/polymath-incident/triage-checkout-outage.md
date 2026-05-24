---
plugin: polymath-incident
scenario: triage-checkout-outage
expect:
  invoked:
    - polymath-incident:incident-triage
  output_matches:
    - "(sev1|sev2)"
    - "Incident Commander"
    - "(Comms|comms)"
    - "(mitigate|diagnose)"
  not_invoked:
    - polymath-incident:postmortem-blameless
timeout_seconds: 90
---

# Prompt

> A pager just fired. Help me triage.

Use polymath-incident:incident-triage. The alert says
"refund p99 latency above SLO" and customers in #support are
reporting refund failures. There's a recent deploy 12 minutes ago.

# Acceptance

- Severity assigned (sev1 or sev2) within the first lines.
- Four roles named (IC, Operator, Comms, Scribe); IC is not also the operator.
- Comms opened (channel + status-page disposition).
- First move (mitigate vs diagnose) is explicit, with verification.
- If diagnose is chosen, a timebox is set.
