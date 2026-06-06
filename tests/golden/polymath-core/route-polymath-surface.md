---
plugin: polymath-core
scenario: route-polymath-surface
expect:
  invoked:
    - polymath-core:route
  output_matches:
    - "\"route_type\""
    - "\"confidence\""
    - "\"evidence\""
    - "\"alternatives\""
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 60
---

# Prompt

> Route this request before doing any work: "Review this PR for
> correctness, security, and missing tests." Return the best Polymath
> workflow or skill as JSON with confidence, evidence, alternatives,
> and next action.

# Acceptance

- The answer invokes `polymath-core:route`.
- The output is JSON or a fenced JSON block with `route_type`,
  `target`, `confidence`, `evidence`, `alternatives`, `question`, and
  `next_action`.
- The preferred target is the `reviewPR` workflow or, if workflow
  approval is missing, the next action asks to propose it before running.
- No implementation, review, file edit, or feature-development work is
  performed by the route step itself.
