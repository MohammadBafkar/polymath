# polymath-finops

FinOps craft: treat cloud cost as an engineering signal — attribute spend, kill waste, and tie cost to units served.

## What it ships

- Skills: `cloud-cost-review` — rightsizing and waste, cost budgets + anomaly alerts, unit economics (cost per request/tenant), reserved/savings-plan coverage, and showback tagging, each recommendation carrying a $ impact.

## Why it exists

The audit found `finops-cost` tagged mostly by *internal* token-accounting skills (`polymath-core:plugin-budget`, `polymath-author:token-budget-report`) — real cloud FinOps was absent. This plugin covers cloud spend specifically and consumes the cost dimension of `polymath-infra-cloud:design-*`.

## Installation

```bash
claude plugin install polymath-finops@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
