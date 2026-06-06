---
plugin: polymath-release
scenario: safe-rollout-new-checkout
expect:
  invoked:
    - polymath-release:safe-rollout
  output_matches:
    - "canary"
    - "rollback"
    - "kill switch"
  not_invoked:
    - polymath-devops:env-promotion
    - polymath-data:run-experiment
timeout_seconds: 90
---

# Prompt

> We're replacing the checkout service and want to roll it out gradually
> with a way to bail instantly if error rates spike.

Use polymath-release:safe-rollout.

# Acceptance

- A rollout technique is chosen (flag/canary/blue-green) with a staged ramp + bake times.
- Health gates tie to an SLI/SLO with an advance threshold; breach triggers automated rollback.
- A kill switch independent of redeploy is specified.
