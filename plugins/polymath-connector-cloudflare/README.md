# polymath-connector-cloudflare

Cloudflare connector for the Polymath marketplace. Triages edge incidents by separating origin / edge / WAF / DNS layers.

## What it ships

- MCP server: Cloudflare MCP server (default: `@cloudflare/mcp-server`) via `npx`.
- Skills: `edge-incident-triage` — status histogram + per-source bucketing + WAF + DNS sanity → layer classification + CF-Ray hint.
- Reference: [`references/cloudflare-tools.md`](references/cloudflare-tools.md).

## Installation

```bash
claude plugin install polymath-connector-cloudflare@polymath \
  --config cloudflareApiToken=<scoped-token> \
  --config cloudflareAccountId=<account-id>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
