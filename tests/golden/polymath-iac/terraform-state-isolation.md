---
plugin: polymath-iac
scenario: terraform-state-isolation
expect:
  invoked:
    - polymath-iac:terraform-state
  output_matches:
    - "(remote backend|S3|locking)"
    - "(blast radius|isolat|per.environment)"
    - "(state mv|import|drift)"
  not_invoked:
    - polymath-cloud:plan-review
timeout_seconds: 120
---

# Prompt

> Our whole infra is in one local Terraform state file and two
> engineers keep clobbering each other's applies. We also can't tell
> when someone changes things in the console. Help me fix the state
> setup.

Use polymath-iac:terraform-state.

# Acceptance

- A remote, locked, encrypted backend replaces local state.
- State is segmented by environment and blast radius (not one monolith), with rationale.
- Drift detection cadence + reconcile policy is defined.
- Safe migration of existing resources via `state mv`/`import` (plan + backup first) is described.
