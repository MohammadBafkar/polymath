---
plugin: polymath-connector-observability
scenario: snapshot-incident
expect:
  invoked:
    - polymath-connector-observability:dashboard-snapshot
  output_matches:
    - "(uid|dashboard)"
    - "(absolute|UTC|2026)"
    - "(snapshot|deleteKey|expires)"
timeout_seconds: 90
---

# Prompt

> Snapshot dashboard refund-api-overview between 2026-05-23T14:00Z and
> 14:30Z with service=refund-api, env=prod. Save under incident
> 2026-09-refund-async.

Use polymath-connector-observability:dashboard-snapshot.

# Acceptance

- Dashboard UID resolved (single match).
- Time captured as absolute UTC timestamps.
- Required template variables specified.
- Snapshot expires set to a finite TTL (not permanent).
- deleteKey saved in artifact file, not echoed in output.
