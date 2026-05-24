---
workflow: deprecationToRemoval
scenario: deprecationToRemoval-v1-refunds
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-content:write-sunset-notice
    - polymath-observability:metrics-design
    - polymath-engineering:feature-dev
    - polymath-engineering:read-code
    - polymath-engineering:verify-change
    - polymath-release:release-notes
  artifacts:
    - "docs/deprecations/v1-refunds.md"
  state_must_pass:
    - notice-exists
    - notice-has-both-dates
    - notice-has-replacement
    - notice-has-usage-section
    - midterm-gate-emitted
    - verify-mentions-tests
timeout_seconds: 900
---

# Prompt

> Stage 1 (announce) of removing POST /v1/refunds, with removal in 6 months.

/polymath-flows:run-workflow deprecationToRemoval capability="POST /v1/refunds endpoint" announceDate=2026-05-24 removalDate=2026-11-24 replacement="POST /v2/refunds" stage=announce

# Acceptance

Announce stage: seven steps run; the deprecation notice exists with
both dates + replacement + usage-baseline section; deprecation
warnings land in code; midterm-gate emits the "skipped (stage=announce)"
summary; release-notes adds a Deprecated entry.

Midterm stage (separate run, months later): the same workflow
invocation with stage=midterm appends a usage-decline row, emits
"midterm-gate: PASS" (or FAIL), and skips the code-change steps.

Remove stage (final run, on or after removalDate): with the previous
midterm-gate PASS in place, the removal step actually deletes the
capability; release-notes adds a Removed (breaking change) entry.
Without PASS or before the date, the removal step is a no-op with a
one-line block reason.
