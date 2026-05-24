---
plugin: polymath-thinking
scenario: pre-mortem-launch
expect:
  invoked:
    - polymath-thinking:pre-mortem
  output_matches:
    - "(failed|failure)"
    - "(likelihood|impact)"
    - "(Top 3|mitigation)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Pre-mortem our rate-limit /login launch in 30 days.

Use polymath-thinking:pre-mortem. The plan is to roll out rate-limiting
to /login behind a feature flag, starting at 10% in a week and 100% in
30 days.

# Acceptance

- 6–10 specific failure modes generated.
- Modes span technical, organizational, user, and operational ranges
  (at least one in each).
- Each mode has explicit likelihood and impact (L/M/H).
- Top 3 picked with concrete, named mitigations (not "be careful").
