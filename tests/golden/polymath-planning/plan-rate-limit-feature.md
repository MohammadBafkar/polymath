---
plugin: polymath-planning
scenario: plan-rate-limit-feature
expect:
  invoked:
    - polymath-planning:write-plan
  artifacts:
    - "docs/plans/rate-limit-login.md"
  output_matches:
    - "What"
    - "Why"
    - "Out of scope"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Write a plan for adding rate-limiting to /login.

Use polymath-planning:write-plan. Title: "Rate-limit /login".
Motivation: brute-force attempts in last week's logs. Constraint: ship
within one sprint.

# Acceptance

- docs/plans/rate-limit-login.md exists with Plan frontmatter.
- All required sections present: What, Why, Approach, Work breakdown,
  Risks, Verification, Out of scope.
- "Out of scope" has at least one entry.
- Plan body ≤ 60 lines total.
