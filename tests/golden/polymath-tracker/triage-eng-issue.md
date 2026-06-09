---
plugin: polymath-tracker
scenario: triage-eng-issue
expect:
  invoked:
    - polymath-tracker:linear-triage
  output_matches:
    - "ENG-"
    - "(issue.update|workflowState|cycle)"
    - "(label|priority|assignee)"
  not_invoked:
    - polymath-tracker:file-bug-from-incident
timeout_seconds: 90
---

# Prompt

> Triage Linear issue ENG-89.

Use polymath-tracker:linear-triage. The issue is in the
ENG team. Title: "Refund p99 latency above SLO". Reporter included
version, 5 reproduction steps, expected vs actual.

# Acceptance

- Type / priority / cycle named.
- Repro judged complete (don't re-ask).
- Action plan names actual MCP tools (issue.update, workflowState.list, comment.create).
- State transition uses an ID (resolved via workflowState.list), not a name.
- Assignee is a person, not a team.
