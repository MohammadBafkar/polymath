---
plugin: polymath-core
scenario: plugin-budget-report
expect:
  invoked:
    - polymath-core:plugin-budget
  not_invoked:
    - polymath-engineering:feature-dev
  output_matches:
    - "tokens"
    - "polymath-core"
timeout_seconds: 60
---

# Prompt

> Report the current Polymath plugin token budget.

Run the polymath-core plugin-budget command and show me the table.

# Acceptance

- A budget table is printed with one row per installed plugin.
- The total tokens are reported.
- No file edits occur.
