---
workflow: deliberationLoop
scenario: deliberationLoop-project-onboarding
expect:
  output_matches:
    - "deliberation"
    - "(tradeoff|trade-off)"
    - "(red-team|objection|risk)"
    - "(plan|validation)"
timeout_seconds: 180
---

# Prompt

> Run `deliberationLoop` with subject "Project onboarding and activation
> for Polymath users" and mode `plan`.

# Acceptance

- The workflow starts with `polymath-thinking:deliberate`.
- Viable alternatives are compared using `polymath-decisions:tradeoff-matrix`.
- A challenge pass names the strongest objection.
- A revised plan includes validation criteria.
