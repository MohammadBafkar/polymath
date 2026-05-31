---
plugin: polymath-deprecation
scenario: deprecate-v1-api
expect:
  invoked:
    - polymath-deprecation:deprecation-plan
  output_matches:
    - "remove"
    - "usage"
  not_invoked:
    - polymath-content:write-sunset-notice
timeout_seconds: 90
---

# Prompt

> We want to retire the v1 search API. Plan the deprecation with a proper
> timeline and a way to make sure we don't pull it while people still use it.

Use polymath-deprecation:deprecation-plan.

# Acceptance

- Two dates (warn + remove) with a justified support window.
- Removal gated on a named usage metric/threshold, not the date alone.
- Exception path + linked migration path present.
