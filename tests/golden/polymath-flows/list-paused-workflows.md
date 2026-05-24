---
plugin: polymath-flows
scenario: list-paused-workflows
expect:
  invoked:
    - polymath-flows:list-workflows
  output_matches:
    - "Paused"
  not_invoked:
    - polymath-flows:run-workflow
timeout_seconds: 60
---

# Prompt

> Show me my paused workflows.

What workflows are paused on this machine?

# Acceptance

- The list is grouped by status (Active / Paused / Completed).
- Each paused entry shows run_id, workflow name, and a one-line
  pause reason if available.
- No state mutation occurs.
