---
plugin: polymath-core
scenario: initialize-project-context
expect:
  invoked:
    - polymath-core:initialize-project
  output_matches:
    - ".polymath/project.yaml"
    - "capabilities"
    - "onboarding"
    - "(tool|env|environment)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> I just installed Polymath in this repo. Inspect README.md, AGENTS.md,
> CLAUDE.md, docs, CI, and project manifests, then create the Polymath
> project context and onboarding package.

Use `polymath-core:initialize-project`. Do not store secret values.

# Acceptance

- `.polymath/project.yaml` is drafted or updated with stack,
  conventions, setup, and recommended Polymath plugins.
- `.polymath/capabilities.yaml` is written only for confidently inferred
  providers.
- `docs/POLYMATH-ONBOARDING.md` names first steps, required tools, env
  var names, useful workflows, and open questions.
