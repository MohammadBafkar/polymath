---
workflow: perfRegression
scenario: perfRegression-refund-p99
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-connector-datadog:query-during-incident
    - polymath-engineering:code-review
    - polymath-engineering:feature-dev
    - polymath-engineering:verify-change
  artifacts:
    - "docs/perf/refund-p99-regression-signals.md"
  state_must_pass:
    - signals-exist
    - signals-baseline-cited
    - verify-mentions-tests
    - fix-summary-mentions-signals
timeout_seconds: 600
---

# Prompt

> Diagnose this perf regression.

/polymath-flows:run-workflow perfRegression title="Refund p99 regression" metric="refund-service P99 latency" suspectSha="abc1234"

Refund p99 latency moved from ~320ms to ~880ms after the 13:50 deploy of
refund-service v0.5.1. Stripe-client error rate is flat.

# Acceptance

- Signals doc compares against a 24h baseline (per the skill).
- Review of the abc1234 diff surfaces perf-sensitive findings or documents
  why the diff isn't the cause.
- Fix step summary cites the signal(s) that motivated the change.
- Verify step summary mentions tests or verification.
