# polymath-connector-azure

Azure connector for the Polymath marketplace. Cli-only — wraps the local `az` CLI for read-only resource inspection.

## What it ships

- Skills: `inspect-azure-resource` — ARM ID → describe + role-assignments + effective-access probe + recent activity-log writes + cost ping.
- Reference: [`references/azure-tools.md`](references/azure-tools.md).

No MCP server: the `az` CLI is the API.

## Pairs with

- `polymath-infra-azure` — write-side IaC. This connector is read-only.

## Installation

```bash
claude plugin install polymath-connector-azure@polymath \
  --config azureSubscription=<sub-id> \
  --config azureLocation=eastus
```

## Dependencies

- `polymath-core`
- Local `az` CLI authenticated.

## License

Apache-2.0.
