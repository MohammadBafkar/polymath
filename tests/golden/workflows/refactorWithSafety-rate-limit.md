---
workflow: refactorWithSafety
scenario: refactorWithSafety-rate-limit
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-engineering:read-code
    - polymath-qa:coverage-gap
    - polymath-qa:unit-tests
    - polymath-engineering:feature-dev
    - polymath-engineering:verify-change
    - polymath-engineering:code-review
  artifacts:
    - "docs/refactors/rate-limit-store-swap-orient.md"
    - "docs/refactors/rate-limit-store-swap-coverage-pre.md"
  state_must_pass:
    - orient-exists
    - coverage-pre-exists
    - verify-mentions-tests
    - review-mentions-simplification
timeout_seconds: 900
---

# Prompt

> Refactor with safety.

/polymath-flows:run-workflow refactorWithSafety title="Rate-limit store swap" scope="api/rate_limit.py"

Goal: swap the in-memory rate-limit store for the new Redis-backed one. No
behavior change for users. Existing tests cover only the happy path.

# Acceptance

- read-code orient lists entry points + change sites.
- coverage-gap surfaces MISSING (unit) items BEFORE any refactor.
- Tests added in `pin-behavior` pass against the un-refactored code.
- Verify confirms every pinning test still passes after the refactor.
- Review explicitly checks for unintended behavior changes.
