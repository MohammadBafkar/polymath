---
plugin: polymath-product
scenario: prd-from-rate-limit-request
expect:
  invoked:
    - polymath-product:prd
  artifacts:
    - "docs/prds/rate-limit-login.md"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 180
---

# Prompt

> Draft a PRD for the rate-limit feature.

We need a PRD for rate-limiting the /login endpoint. Five attempts
per minute per IP, then a 15-minute cool-down. Audience is the
platform team. Save it to docs/prds/rate-limit-login.md.

# Acceptance

- docs/prds/rate-limit-login.md exists.
- The PRD has frontmatter with `artifact: PRD`, `title`, `status`,
  `owner`, `created`.
- Sections present: Problem, Users / customers, Goals, Non-goals,
  Requirements, Acceptance criteria, Metrics, Risks and open
  questions, Rollout plan, References.
- At least one non-goal is listed.
- At least one open question or risk is listed.
- No implementation language in Goals or Requirements.
