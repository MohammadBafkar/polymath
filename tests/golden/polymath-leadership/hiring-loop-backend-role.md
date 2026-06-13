---
plugin: polymath-leadership
scenario: hiring-loop-backend-role
expect:
  invoked:
    - polymath-leadership:hiring-loop
  output_matches:
    - "(scorecard|competenc)"
    - "(calibrat|rubric|standardiz)"
    - "(evidence|debrief)"
  not_invoked:
    - polymath-leadership:perf-review
timeout_seconds: 120
---

# Prompt

> Help me design the interview loop for a senior backend hire. Right
> now interviewers ask whatever they want and we decide on vibes in
> the debrief.

Use polymath-leadership:hiring-loop.

# Acceptance

- A role scorecard of 4–6 competencies is defined first, with a per-stage signal map (minimal overlap, full coverage).
- Questions/rubrics standardized within a stage; past-behavior over hypotheticals.
- Written evidence submitted before the debrief; the decision is scorecard-anchored with an owner.
- Bias guards (consistent process, diverse panel, funnel metrics) are included.
