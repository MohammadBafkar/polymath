---
plugin: polymath-communication
scenario: sunset-old-refund-endpoint
expect:
  invoked:
    - polymath-communication:write-sunset-notice
  artifacts:
    - "docs/sunsets/refunds-v1-endpoint.md"
  output_matches:
    - "(sunset|deprecation)"
    - "(removal)"
    - "(replace|replacement)"
    - "Before"
    - "After"
  not_invoked:
    - polymath-communication:write-advisory
timeout_seconds: 90
---

# Prompt

> Write a sunset notice for our old refund endpoint.

Use polymath-communication:write-sunset-notice. Capability: POST /v1/refunds.
Sunset date: 2026-09-01 (warning + new-usage blocked). Removal date:
2026-12-01. Replacement: POST /v1/orders/<order_id>/refunds.

# Acceptance

- Both dates present (sunset and removal).
- Before / after code example.
- Replacement named with a one-line comparison.
- Out-of-scope section reassures readers what is NOT changing.
- Exception path documented for customers who need an extension.
- FAQ with 3 anticipated questions.
