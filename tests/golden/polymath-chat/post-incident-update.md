---
plugin: polymath-chat
scenario: post-incident-update
expect:
  invoked:
    - polymath-chat:post-incident-comms
  output_matches:
    - "(channel|thread_ts|chat_postMessage)"
    - "(thread|ts)"
  not_invoked:
    - polymath-chat:post-async-update
timeout_seconds: 90
---

# Prompt

> Post an incident-comms update to Slack.

Use polymath-chat:post-incident-comms. Incident ID:
inc-2026-09. Update body (from polymath-incident:comms-update):
status=identified, refund rollback in progress, next update in 15 min.
Default incident channel: incidents.

# Acceptance

- Channel resolved to an ID (not a name).
- Thread root saved as an artifact for the next update.
- Sev1/Sev2 mirror to the status-page channel as a one-liner with a back-pointer.
- No PII in the fallback `text` field.
