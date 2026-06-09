# polymath-connector-statuspage

Statuspage (Atlassian) connector for the Polymath marketplace. Translates internal incident comms into customer-facing public updates.

## What it ships

- MCP server: Statuspage MCP server (default: `@statuspage/mcp-server`) via `npx`.
- Skills: `post-statuspage-update` — severity → public-impact mapping, component scoping, customer-safe body rewrite.
- Reference: [`references/statuspage-tools.md`](references/statuspage-tools.md).

## Pairs with

- [`polymath-incident`](../polymath-incident/README.md) — `comms-update` writes the internal body; this plugin posts the external one.

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** This connector's `.mcp.json` names
> `@statuspage/mcp-server`, which does **not** resolve on npm as of 2026-06-08,
> so `npx -y @statuspage/mcp-server` will fail to start. There is no official
> Statuspage MCP server yet (the policy notes the Statuspage REST API) —
> substitute a real command in `.mcp.json` before relying on this connector.
> This is part of why the connector is `status: experimental`. See
> [`docs/CONNECTOR-POLICY.md` §4.2](../../docs/CONNECTOR-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-connector-statuspage@polymath \
  --config statuspageApiKey=<key> \
  --config statuspagePageId=<page-id>
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** No official MCP yet (Atlassian Statuspage REST API)
- **Polymath value:** Incident-comms drafting tied to severity ladder
- **Sunset trigger:** Demote when Statuspage ships an official MCP and our wrapper has no delta.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
