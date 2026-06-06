---
plugin: polymath-planning
scenario: prioritize-onboarding-backlog
expect:
  invoked:
    - polymath-planning:prioritize
  artifacts:
    - "docs/prioritization/onboarding-backlog.md"
  output_matches:
    - "RICE"
    - "Confidence"
    - "Now"
  not_invoked:
    - polymath-planning:estimate
    - polymath-product:decompose-epic
timeout_seconds: 90
---

# Prompt

> We have five onboarding-improvement ideas and limited capacity this
> quarter — rank them and tell me what to do now vs later. Reach/impact
> guesses are in the doc; effort is rough t-shirt sizes.

Use polymath-planning:prioritize. Slug: "onboarding-backlog".

# Acceptance

- docs/prioritization/onboarding-backlog.md exists.
- A method is named with a one-line rationale (RICE for a product backlog).
- The scored table shows the inputs (reach/impact/confidence/effort) per item, not just a composite number.
- Low-confidence rows are flagged and a Now/Next/Later cut is present.
