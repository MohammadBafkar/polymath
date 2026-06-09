---
plugin: polymath-tracker
scenario: triage-bug-ticket
expect:
  invoked:
    - polymath-tracker:jira-triage
  output_matches:
    - "PROJ-1234"
    - "(jira_update_issue|jira_add_comment|jira_transition_issue)"
  not_invoked:
    - polymath-tracker:file-bug-from-incident
timeout_seconds: 90
---

# Prompt

> Triage PROJ-1234.

Use polymath-tracker:jira-triage. The issue is a bug:
"Refund p99 latency above SLO since v0.5.1 deploy". The reporter
included version, 5 reproduction steps, and expected vs actual.
Component should be `payments-api`.

# Acceptance

- Classification names "Bug" with severity / priority.
- Repro is judged complete (don't re-ask for it).
- jira_update_issue / jira_transition_issue (or equivalent MCP tool names) appear in the action plan.
- Routing names a team handle, not a person.
