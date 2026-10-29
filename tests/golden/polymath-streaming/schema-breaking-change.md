---
plugin: polymath-streaming
scenario: schema-breaking-change
expect:
  invoked:
    - polymath-streaming:event-schema-evolution
  output_matches:
    - "(expand|dual|migrate|contract)"
    - "(BACKWARD|compatib)"
    - "(upcast|replay|deprecat)"
timeout_seconds: 120
---

# Prompt

> We want to replace the 'total' dollar field on OrderPlaced with amount_minor and currency. Four services consume the topic and the lake replays full history. How do we roll this out safely?

Use polymath-streaming:event-schema-evolution.

# Acceptance

- Treats the change as breaking and uses expand-migrate-contract.
- Compatibility mode matches replay (transitive).
- CI compatibility and contract checks.
