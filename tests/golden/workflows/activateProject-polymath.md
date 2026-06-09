---
workflow: activateProject
scenario: activateProject-polymath
expect:
  output_matches:
    - ".polymath/project.yaml"
    - "docs/POLYMATH-ONBOARDING.md"
    - "(setup|tools|environment)"
timeout_seconds: 180
---

# Prompt

> Run the `activateProject` workflow for the Polymath marketplace repo.

# Acceptance

- The workflow invokes `polymath-core:initialize-project`.
- A project context file is produced with stack, conventions, setup,
  and Polymath recommendations.
- Onboarding notes explain first steps, tool checks, env var names,
  useful workflows, and unresolved questions.
