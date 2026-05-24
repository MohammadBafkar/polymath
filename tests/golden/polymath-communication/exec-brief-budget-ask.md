---
plugin: polymath-communication
scenario: exec-brief-budget-ask
expect:
  invoked:
    - polymath-communication:exec-brief
  artifacts:
    - "docs/briefs/q3-platform-investment.md"
  output_matches:
    - "(TL;DR|Bottom line)"
    - "(recommend|recommendation)"
    - "(yes|approve|ask)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Write a BLUF brief asking the CTO for Q3 platform-team investment.

Use polymath-communication:exec-brief. Title: "Q3 platform investment".
Audience: CTO. Ask: approve a 3-person hire + $50k tooling budget. Evidence:
deploy frequency dropped 40% YoY, on-call burden up.

# Acceptance

- TL;DR comes first and makes sense if the reader stops there.
- ONE recommendation, not a menu.
- Ask is unambiguous (number of hires + budget).
- "What if no" cost stated.
- No background section; references at the bottom.
