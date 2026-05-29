---
plugin: polymath-thinking
scenario: deliberate-plugin-activation
expect:
  invoked:
    - polymath-thinking:deliberate
  output_matches:
    - "(Observations|observe)"
    - "(Options|alternatives)"
    - "(Trade-offs|criteria)"
    - "(Recommendation|revised plan)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> We need to decide whether Polymath should add project activation as a
> core skill, a workflow, or a separate plugin. Think through it
> iteratively with incomplete data, compare alternatives, stress-test the
> leading answer, and revise if needed.

Use `polymath-thinking:deliberate`.

# Acceptance

- Facts, assumptions, unknowns, and constraints are separated.
- At least five options are considered, including doing nothing or
  deferring.
- Trade-off criteria are explicit.
- The strongest objection and validation plan are named.
