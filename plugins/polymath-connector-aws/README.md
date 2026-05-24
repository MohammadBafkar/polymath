# polymath-connector-aws

AWS connector for the Polymath marketplace. Cli-only — wraps the local `aws` CLI for read-only resource inspection.

## What it ships

- Skills: `inspect-aws-resource` — ARN → state + effective permissions (simulator) + recent CloudTrail + 7-day cost.
- Reference: [`references/aws-tools.md`](references/aws-tools.md).

No MCP server: the `aws` CLI is the API.

## Pairs with

- `polymath-infra-aws` — write-side IaC patterns. This connector is read-only.

## Installation

```bash
claude plugin install polymath-connector-aws@polymath \
  --config awsProfile=prod-payments \
  --config awsRegion=us-east-1
```

## Dependencies

- `polymath-core`
- Local `aws` CLI configured with the named profile.

## License

Apache-2.0.
