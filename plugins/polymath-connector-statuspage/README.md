# polymath-connector-statuspage

Statuspage (Atlassian) connector for the Polymath marketplace. Translates internal incident comms into customer-facing public updates.

## What it ships

- MCP server: Statuspage MCP server (default: `@statuspage/mcp-server`) via `npx`.
- Skills: `post-statuspage-update` — severity → public-impact mapping, component scoping, customer-safe body rewrite.
- Reference: [`references/statuspage-tools.md`](references/statuspage-tools.md).

## Pairs with

- [`polymath-incident`](../polymath-incident/README.md) — `comms-update` writes the internal body; this plugin posts the external one.

## Installation

```bash
claude plugin install polymath-connector-statuspage@polymath \
  --config statuspageApiKey=<key> \
  --config statuspagePageId=<page-id>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
