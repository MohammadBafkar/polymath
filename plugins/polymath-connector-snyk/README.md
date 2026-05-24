# polymath-connector-snyk

Snyk connector for the Polymath marketplace.

## What it ships

- MCP server: Snyk MCP server (default: `@snyk/mcp-server`) via `npx`.
- Skills: `triage-vulns`.
- Hooks: `Stop` — when `.snyk.last.json` (cached `snyk test` output) shows open critical findings, nudge the user.
- Reference: [`references/snyk-tools.md`](references/snyk-tools.md).

## Installation

```bash
claude plugin install polymath-connector-snyk@polymath
# You'll be prompted for snykToken (sensitive). snykOrg is optional.
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
