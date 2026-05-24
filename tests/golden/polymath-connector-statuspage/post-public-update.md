---
plugin: polymath-connector-statuspage
scenario: post-public-update
expect:
  invoked:
    - polymath-connector-statuspage:post-statuspage-update
  output_matches:
    - "(component_ids|cmp_)"
    - "(critical|major|minor)"
    - "(investigating|identified|monitoring|resolved)"
timeout_seconds: 90
---

# Prompt

> Post a sev2 Statuspage update for incident 2026-09-refund-async,
> phase "identified", affecting refund-api and refund-worker.

Use polymath-connector-statuspage:post-statuspage-update. The
internal comms-update body mentions on-call handles and a Linear
ticket — strip them for the public version.

# Acceptance

- Severity sev2 → impact `major`.
- Component IDs resolved (not posted by component name).
- Public body free of internal handles, ticket IDs, codenames.
- Phase `identified` posted with the correct Statuspage status verb.
