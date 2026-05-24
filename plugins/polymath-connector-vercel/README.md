# polymath-connector-vercel

Vercel connector for the Polymath marketplace. Triages deployments with build + runtime + edge evidence.

## What it ships

- MCP server: Vercel MCP server (default: `@vercel/mcp-server`) via `npx`.
- Skills: `inspect-deployment` — classify healthy / degraded / broken; rollback target identified (previous READY production).
- Reference: [`references/vercel-tools.md`](references/vercel-tools.md).

## Installation

```bash
claude plugin install polymath-connector-vercel@polymath --config vercelToken=<token>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
