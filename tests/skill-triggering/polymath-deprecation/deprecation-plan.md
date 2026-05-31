---
plugin: polymath-deprecation
skill: deprecation-plan
trigger_prompts:
  - "we need to retire the v1 API — plan the deprecation timeline"
  - "how do we sunset this feature without breaking people who still use it"
  - "set up a deprecation schedule with a warn and remove date"
must_invoke:
  - polymath-deprecation:deprecation-plan
allow_invoke:
  - polymath-deprecation:*
  - polymath-content:*
  - polymath-core:*
forbidden_prompts:
  - "write the customer-facing sunset notice for this"
  - "write the upgrade steps for consumers moving off v1"
---

# Why this test exists

Deprecation-timeline phrasings route here. Forbidden prompts guard against
`polymath-content:write-sunset-notice` (the notice) and the sibling
`migration-guide` (consumer steps).
