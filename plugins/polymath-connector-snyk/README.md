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

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Snyk MCP
- **Polymath value:** `triage-vulns` classification (exploitable / reachable / dev-only); Stop hook warns on critical findings
- **Sunset trigger:** Demote when Snyk MCP ships classification + open-criticals surfacing.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
