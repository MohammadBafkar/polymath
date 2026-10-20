# polymath-vuln-scan

Snyk connector for the Polymath marketplace.

## What it ships

- MCP server template: Snyk MCP server (default: `@snyk/mcp-server`) — rendered
  to your host's MCP config only when you opt in; if your agent already has a
  Snyk MCP registered, it is reused.
- Skills: `triage-vulns`.
- Hooks: `Stop` — when `.snyk.last.json` (cached `snyk test` output) shows open critical findings, nudge the user.
- Reference: [`references/snyk-tools.md`](references/snyk-tools.md).

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** This connector's server template
> (`mcp/servers.json`) names `@snyk/mcp-server`, which does **not** resolve on
> npm as of 2026-06-08, so the rendered `npx -y @snyk/mcp-server` fragment would
> fail to start. Snyk's MCP support ships via the `snyk` CLI (e.g. a `snyk mcp`
> subcommand), not this npm package — substitute the real command before
> installing a rendered fragment. If your host agent already has a Snyk MCP
> registered, it is reused and no template is needed. This is part of why the
> connector is `status: experimental`. See
> [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-vuln-scan@polymath
# You'll be prompted for snykToken (sensitive). snykOrg is optional.
```

MCP servers are not auto-registered. If your agent already has a Snyk MCP
registered, the skills use it. Otherwise run
`python3 tools/mcp-registry.py render --plugin polymath-vuln-scan --target <your-host>`
and apply the fragment to your host's MCP config.

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `vulnerability_scanner` — Snyk, Dependabot, GitHub Advanced Security
- **Polymath value:** `triage-vulns` classification (exploitable / reachable / dev-only); Stop hook warns on critical findings
- **Sunset trigger:** Demote when an official MCP ships classification + open-criticals surfacing.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
