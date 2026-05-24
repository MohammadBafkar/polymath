# polymath-connector-datadog

Datadog connector for the Polymath marketplace.

## What it ships

- MCP server: Datadog MCP server (default: `@datadog/mcp-server`) via `npx`.
- Skills: `author-monitor`, `query-during-incident`.
- Reference: [`references/datadog-tools.md`](references/datadog-tools.md).

## Installation

```bash
claude plugin install polymath-connector-datadog@polymath
# You'll be prompted for datadogApiKey + datadogAppKey + datadogSite (sensitive).
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
