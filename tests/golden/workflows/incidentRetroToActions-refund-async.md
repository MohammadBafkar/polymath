---
workflow: incidentRetroToActions
scenario: incidentRetroToActions-refund-async
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-engineering:read-code
    - polymath-incident:postmortem-blameless
    - polymath-planning:work-breakdown
    - polymath-planning:estimate
    - polymath-connector-jira:file-bug-from-incident
    - polymath-engineering:feature-dev
    - polymath-engineering:code-review
  artifacts:
    - "docs/retros/refund-async-actions-raw.md"
    - "docs/retros/refund-async-actions-classified.md"
    - "docs/retros/refund-async-breakdown.md"
    - "docs/retros/refund-async-estimates.md"
    - "docs/retros/refund-async-tickets.md"
  state_must_pass:
    - actions-raw-exists
    - breakdown-exists
    - estimates-exists
    - tickets-exists
    - classification-uses-categories
    - tickets-list-has-keys
    - review-confirms-tracking
timeout_seconds: 900
---

# Prompt

> Decompose docs/postmortems/2026-09-refund-async.md into trackable
> action items.

/polymath-flows:run-workflow incidentRetroToActions postmortemPath=docs/postmortems/2026-09-refund-async.md

# Acceptance

End-to-end: seven steps run, every step writes a summary, all seven
mustPass checks pass. Every action item in the source postmortem
ends up with an ENG-style ticket key in `…-tickets.md`, the
postmortem file is updated with those ticket keys back-linked, and
the review step explicitly confirms tracking.

Blame-shaped wording in the original postmortem (e.g. "Alex should have
known") is rewritten as a system-shaped action (e.g. "Refund worker
lacks a circuit breaker between retries"); the classification step
catches this and the review step confirms none remain.
