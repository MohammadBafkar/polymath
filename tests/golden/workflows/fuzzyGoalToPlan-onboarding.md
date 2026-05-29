---
workflow: fuzzyGoalToPlan
scenario: fuzzyGoalToPlan-onboarding
expect:
  output_matches:
    - "docs/thinking/.*-framing.md"
    - "docs/maps/"
    - "docs/plans/.*-breakdown.md"
    - "docs/plans/"
    - "([Aa]ssumption|[Uu]nknown)"
  timeout_seconds: 240
---

# Prompt

> Make onboarding faster. That's the whole brief — it's vague on purpose.
>
> Run `/polymath-flows:run-workflow fuzzyGoalToPlan goal="make onboarding faster"`.

# Acceptance

- The framing step disambiguates the goal, separating facts from assumptions and
  naming the unknowns plus the evidence that would change the plan.
- A story map produces vertical shippable slices with a walking skeleton.
- The work breakdown names the critical path and avoids bare "investigate" steps.
- The estimate is three-point with a range, flagging poorly scoped steps.
- The final plan quotes the assumptions and lists explicit out-of-scope items.
