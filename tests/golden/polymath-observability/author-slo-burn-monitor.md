---
plugin: polymath-observability
scenario: author-slo-burn-monitor
expect:
  invoked:
    - polymath-observability:author-monitor
  output_matches:
    - "(metric alert|service check|log alert)"
    - "(threshold|critical)"
    - "(notify_no_data|no-data)"
    - "@pagerduty"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Author a Datadog monitor for the refund-service P99 latency SLO.

Use polymath-observability:author-monitor. The SLO is
99.5% / 28d with a 500ms P99 latency threshold. Page the
@pagerduty-payments service on sev2 burn.

# Acceptance

- Monitor type chosen explicitly (metric alert).
- Threshold matches the SLO (500ms = 0.5s).
- Evaluation window is short for paging (5-15 min).
- notify_no_data explicitly set, with rationale.
- Notification message routes via @pagerduty-payments and includes the runbook link placeholder.
- Tags include team / service / severity / slo.
