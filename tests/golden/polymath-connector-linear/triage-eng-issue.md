---
plugin: polymath-connector-linear
scenario: triage-eng-issue
expect:
  invoked:
    - polymath-connector-linear:linear-triage
  output_matches:
    - "ENG-"
    - "(issue.update|workflowState|cycle)"
    - "(label|priority|assignee)"
  not_invoked:
    - polymath-connector-linear:file-bug-from-incident
timeout_seconds: 90
---

# Prompt

> Triage Linear issue ENG-89.

Use polymath-connector-linear:linear-triage. The issue is in the
ENG team. Title: "Refund p99 latency above SLO". Reporter included
version, 5 reproduction steps, expected vs actual.

# Acceptance

- Type / priority / cycle named.
- Repro judged complete (don't re-ask).
- Action plan names actual MCP tools (issue.update, workflowState.list, comment.create).
- State transition uses an ID (resolved via workflowState.list), not a name.
- Assignee is a person, not a team.
