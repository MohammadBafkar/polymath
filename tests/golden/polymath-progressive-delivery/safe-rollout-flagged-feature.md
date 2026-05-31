---
plugin: polymath-progressive-delivery
scenario: safe-rollout-new-checkout
expect:
  invoked:
    - polymath-progressive-delivery:safe-rollout
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

Use polymath-progressive-delivery:safe-rollout.

# Acceptance

- A rollout technique is chosen (flag/canary/blue-green) with a staged ramp + bake times.
- Health gates tie to an SLI/SLO with an advance threshold; breach triggers automated rollback.
- A kill switch independent of redeploy is specified.
