# polymath-connector-grafana

Grafana connector for the Polymath marketplace. Captures permalinked dashboard snapshots for incident timelines and postmortem evidence.

## What it ships

- MCP server: Grafana MCP server (default: `@grafana/mcp-server`) via `npx`.
- Skills: `dashboard-snapshot` — absolute time + variables pinned, finite TTL, deleteKey saved as an artifact.
- Reference: [`references/grafana-tools.md`](references/grafana-tools.md).

## Installation

```bash
claude plugin install polymath-connector-grafana@polymath \
  --config grafanaUrl=https://grafana.example.com \
  --config grafanaApiKey=<service-account-token>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
