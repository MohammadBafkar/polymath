# polymath-infra-terraform-stack

Terraform composition craft for the Polymath marketplace.

## What it ships

- Skills: `design-stack-composition` — pick module boundaries, state layout, workspace strategy, remote-state plumbing with blast-radius per apply.
- Command: `/polymath-infra-terraform-stack:design`.

## Pairs with

- `polymath-connector-terraform` — review individual plan output before apply.
- `polymath-infra-aws` / `polymath-infra-gcp` / `polymath-infra-azure` — cloud-specific primitive choice.

## Installation

```bash
claude plugin install polymath-infra-terraform-stack@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
