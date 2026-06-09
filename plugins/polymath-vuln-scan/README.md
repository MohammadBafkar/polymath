# polymath-vuln-scan

Snyk connector for the Polymath marketplace.

## What it ships

- MCP server: Snyk MCP server (default: `@snyk/mcp-server`) via `npx`.
- Skills: `triage-vulns`.
- Hooks: `Stop` — when `.snyk.last.json` (cached `snyk test` output) shows open critical findings, nudge the user.
- Reference: [`references/snyk-tools.md`](references/snyk-tools.md).

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** This connector's `.mcp.json` names
> `@snyk/mcp-server`, which does **not** resolve on npm as of 2026-06-08, so
> `npx -y @snyk/mcp-server` will fail to start. Snyk's MCP support ships via the
> `snyk` CLI (e.g. a `snyk mcp` subcommand), not this npm package — substitute
> the real command in `.mcp.json` before relying on this connector. This is part
> of why the connector is `status: experimental`. See
> [`docs/CONNECTOR-POLICY.md` §4.2](../../docs/CONNECTOR-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-vuln-scan@polymath
# You'll be prompted for snykToken (sensitive). snykOrg is optional.
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `vulnerability_scanner` — Snyk, Dependabot, GitHub Advanced Security
- **Polymath value:** `triage-vulns` classification (exploitable / reachable / dev-only); Stop hook warns on critical findings
- **Sunset trigger:** Demote when an official MCP ships classification + open-criticals surfacing.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
