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

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Datadog MCP
- **Polymath value:** Incident-shaped read-only query patterns; monitor authoring discipline
- **Sunset trigger:** Demote when Datadog MCP adds a workflow-quality query language.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

Apache-2.0.
