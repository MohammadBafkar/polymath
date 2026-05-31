# polymath-progressive-delivery

Progressive delivery craft: get a risky change to users gradually with the rollback reflex built in, instead of an all-at-once deploy.

## What it ships

- Skills: `safe-rollout` — design a progressive rollout (feature-flag strategy, canary / blue-green / ring stages, SLO-driven health gates, automated rollback, kill switch) and call out irreversible data changes a flag can't undo.

## Why it exists

The catalog audit found "deployment" covered only by `polymath-devops:env-promotion` (build → environment). Nothing designed *how* a change reaches users safely once it's in an environment — flags, canary, rollback. This plugin fills that delivery-safety gap and consumes `polymath-sre:slo-design` for its health gates.

## Installation

```bash
claude plugin install polymath-progressive-delivery@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
