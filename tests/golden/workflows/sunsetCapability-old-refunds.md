---
workflow: sunsetCapability
scenario: sunsetCapability-old-refunds
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-content:write-sunset-notice
    - polymath-engineering:feature-dev
    - polymath-engineering:verify-change
    - polymath-release:release-notes
  artifacts:
    - "docs/sunsets/post-v1-refunds-endpoint.md"
  state_must_pass:
    - sunset-notice-exists
    - notice-has-both-dates
    - notice-has-replacement
    - verify-mentions-tests
timeout_seconds: 600
---

# Prompt

> Sunset our old POST /v1/refunds endpoint.

/polymath-flows:run-workflow sunsetCapability capability="POST /v1/refunds endpoint" sunsetDate="2026-09-01" removalDate="2026-12-01" replacement="POST /v1/orders/<order_id>/refunds" stage="announce"

# Acceptance

- Sunset notice contains both dates and the replacement.
- Deprecate-in-code step adds deprecation warnings (log line / response
  header) — does NOT remove the endpoint at announce stage.
- Remove step no-ops at announce stage with a one-line explanation.
- Verify confirms calls to /v1/refunds still work but emit the warning.
- Release-notes adds a deprecation entry pointing to the sunset notice.
