---
plugin: polymath-observability
scenario: triage-spike-after-deploy
expect:
  invoked:
    - polymath-observability:triage-error
  output_matches:
    - "(SPIKE|trend|baseline)"
    - "(deploy|correlat|first.seen)"
    - "(FIX|INVESTIGATE|IGNORE|RE-PRIORITIZE)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Triage this Sentry issue.

Use polymath-observability:triage-error. Issue:
https://example.sentry.io/issues/12345/

Title: RefundServiceException: Stripe timeout.
First seen: 13:52 UTC (3 min after the 13:50 deploy of refund-service v0.5.1).
Event count: 1,420 in last 24h (0 the prior 24h — new error).
Users affected: 240 distinct, production env.
Customer-facing path.

# Acceptance

- Trend computed against the 24h baseline (1,420 vs 0).
- Recent-deploy correlation named explicitly with the deploy version.
- ONE action chosen (FIX NOW / FIX THIS SPRINT / INVESTIGATE / IGNORE+suppression / RE-PRIORITIZE).
- If IGNORE, must pair with a suppression rule + tracking ticket.
- Action recommends consulting polymath-incident:incident-triage when sev2+.
