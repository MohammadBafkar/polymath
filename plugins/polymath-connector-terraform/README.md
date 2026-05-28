# polymath-connector-terraform

Terraform / OpenTofu connector for the Polymath marketplace. Reviews `terraform plan` output for destructive changes, drift, and unsafe diffs.

## What it ships

- Skills: `plan-review` — classifies every resource change, flags destructive patterns by resource type, separates drift from intent, and outputs a categorized go/no-go.
- Reference: [`references/terraform-tools.md`](references/terraform-tools.md).

No MCP server: Terraform's CLI is the API, and this connector calls it locally (binary configurable via `userConfig.terraformBinary`).

## Pairs with

- `polymath-infra-cloud` — ships the *write* side (cloud-pattern selection for AWS / GCP / Azure / Terraform stack composition); this plugin reviews the *plan* side before apply.

## Installation

```bash
claude plugin install polymath-connector-terraform@polymath
# optional:
# claude plugin install polymath-connector-terraform@polymath --config terraformBinary=tofu
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
