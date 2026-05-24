---
plugin: polymath-engineering
scenario: read-code-orientation
expect:
  invoked:
    - polymath-engineering:read-code
  output_matches:
    - "Entry points"
    - "Likely change site"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Orient me in the polymath-flows plugin.

I want to add a new mustPass check type to polymath-flows. Where
should it land? Use the read-code skill to orient me.

# Acceptance

- The summary lists at least one entry point under bin/polymath-flow.
- The "Likely change site" cites the _run_check function with a file
  path and line number.
- The summary is ≤ 30 lines.
- At least one open question is recorded.
- No code edits occur during orientation.
