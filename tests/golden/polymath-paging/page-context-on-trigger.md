---
plugin: polymath-paging
scenario: page-context-on-trigger
expect:
  invoked:
    - polymath-paging:page-context
  output_matches:
    - "(PT[A-Z0-9]+|incident ID)"
    - "Since"
    - "(Recent change|recent deploys|What changed)"
    - "First check"
  not_invoked:
    - polymath-incident:postmortem-blameless
timeout_seconds: 90
---

# Prompt

> Pager fired. Pull context for incident PT9X3HQ7.

Use polymath-paging:page-context. Triggered at
2026-05-24 14:02 UTC by Datadog monitor "refund-p99-500ms". A
deploy of refund-service to prod happened at 13:50 (refund:0.5.1).

# Acceptance

- Time-elapsed-since-trigger computed (not "recent").
- Assigned responder named + next-up escalation.
- "Recent change" lists the 13:50 deploy.
- A single first-check recommendation, not a checklist of 5.
- No speculation about root cause from the title alone.
