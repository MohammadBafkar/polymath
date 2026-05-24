# polymath-connector-gcp

GCP connector for the Polymath marketplace. Cli-only — wraps the local `gcloud` CLI for read-only resource inspection.

## What it ships

- Skills: `inspect-gcp-resource` — full resource path → describe + IAM policy + effective permissions + recent audit-log writes + cost ping.
- Reference: [`references/gcp-tools.md`](references/gcp-tools.md).

No MCP server: the `gcloud` CLI is the API.

## Pairs with

- `polymath-infra-gcp` — write-side IaC. This connector is read-only.

## Installation

```bash
claude plugin install polymath-connector-gcp@polymath \
  --config gcpProject=example-prod \
  --config gcpRegion=us-central1
```

## Dependencies

- `polymath-core`
- Local `gcloud` CLI authenticated.

## License

Apache-2.0.
