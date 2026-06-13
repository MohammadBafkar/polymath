# polymath-sre

SRE craft for the Polymath marketplace.

## What it ships

- Skills: `slo-design`, `error-budget-policy`, `chaos-experiment`, `capacity-plan`, `demand-forecast`, `oncall-design`.

`demand-forecast` projects capacity demand forward in time (growth/seasonal models, must-provision-by date) — the forward-looking complement to the point-in-time `capacity-plan`. `oncall-design` runs the on-call program (rotation, alert quality, runbook coverage, toil budget, operational review).

## Installation

```bash
claude plugin install polymath-sre@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
