---
artifact: Postmortem
schemaVersion: 0.1
incident_id: "{{incident_id}}"
severity: "{{severity}}"
status: draft
facilitator: "{{facilitator}}"
occurred: "{{occurred_iso}}"
resolved: "{{resolved_iso}}"
duration_minutes: 0
blameless: true
---

# Postmortem: {{incident_title}}

## Summary

One paragraph: what failed, who noticed first, how long, what the user experience was.

## Impact

- Users affected: …
- Revenue impact: … (or "none observable")
- Internal impact: …

## Timeline

All times UTC.

| Time | Event |
| ---- | ----- |
| 14:02 | First metric anomaly — refund p99 latency above SLO. |
| 14:05 | Pager fires. |
| 14:08 | On-call ack. |
| 14:12 | Mitigation: revert to previous image tag. |
| 14:18 | Metrics recovered. |
| 14:25 | Incident resolved. |

## Root cause

Apply the 5-whys (see `polymath-thinking:5-whys`). Land on the system-level
cause, not "Alice forgot". Cite evidence.

## What went well

- …
- …

## What went poorly

- …
- …

## Where we got lucky

- …

## Action items

Each action has an owner (team), a due date, and a tracking link. No bare "improve X".

| # | Action | Owner | Due | Link |
| - | ------ | ----- | --- | ---- |
| 1 | Add burn-rate alert at 6h window | payments-sre | 2026-06-10 | ISSUE-123 |
| 2 | Add canary stage to refund deploy pipeline | platform | 2026-06-15 | ISSUE-124 |

## Blameless statement

This postmortem is blameless. Names appear only as roles ("on-call", "deployer", "reviewer") unless the person explicitly requested otherwise.

## References

- Runbook: `{{runbook_link}}`
- Dashboard: `{{dashboard_link}}`
- Related ADRs: …
