---
plugin: polymath-qa
scenario: coverage-gap-for-diff
expect:
  invoked:
    - polymath-qa:coverage-gap
  output_matches:
    - "(Covered|MISSING)"
    - "(unit|integration)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Check the diff for missing test coverage.

Use polymath-qa:coverage-gap. The diff adds two new branches in
`api/rate_limit.py`: window reset at exactly the boundary, and refund
exceeding the order's refundable total. Existing tests cover only the
happy path.

# Acceptance

- Each new behavior is paired with Covered / MISSING (unit) / MISSING (integration) / WEAK.
- Each MISSING item nominates a concrete test name.
- Coverage % is not invented (no claim like "coverage went from 80% to 60%").
- Suggested tests target the *new* branches, not the existing happy path.
