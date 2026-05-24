---
plugin: polymath-connector-cloudflare
scenario: triage-502s
expect:
  invoked:
    - polymath-connector-cloudflare:edge-incident-triage
  output_matches:
    - "(origin|edge|worker)"
    - "(WAF|firewall|DNS)"
    - "(CF.Ray|ray|classification)"
timeout_seconds: 90
---

# Prompt

> Triage intermittent 502s on refund.example.com over the last 30 minutes.

Use polymath-connector-cloudflare:edge-incident-triage.

# Acceptance

- Status histogram surfaced before classification.
- Per-source bucketing (origin / worker / edge).
- WAF + DNS sanity at least checked.
- Classification is one of origin-failure / edge-failure / waf-block / dns-misconfig / mixed.
- A CF-Ray sample provided for downstream origin-log filtering.
