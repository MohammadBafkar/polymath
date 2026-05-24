---
plugin: polymath-leadership
scenario: perf-review-senior-engineer
expect:
  invoked:
    - polymath-leadership:perf-review
  artifacts:
    - "docs/people/alice/perf-h1-2026.md"
  output_matches:
    - "(Impact|Strengths|growth)"
    - "(promote|exceeds|meets|below)"
  not_invoked:
    - polymath-leadership:one-on-one-prep
timeout_seconds: 120
---

# Prompt

> Write a performance review for Alice for H1 2026.

Use polymath-leadership:perf-review. Employee: Alice. Manager: me.
Cycle: H1 2026. Level: Senior Engineer. Use the linked career ladder.
Evidence comes from 6 months of 1:1 notes plus 360 feedback.

# Acceptance

- Impact section has 3–5 outcomes with evidence (metric / artifact).
- "How they worked" cites specific incidents, not adjectives.
- Areas-for-growth section: each item is something Alice already heard in 1:1s. No surprise feedback.
- Recommendation (promote / exceeds / meets / below) anchored in the level expectations.
- Calibration notes flag at least one bias risk (recency, halo, etc.).
