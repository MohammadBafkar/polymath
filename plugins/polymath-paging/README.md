# polymath-paging

PagerDuty connector for the Polymath marketplace.

## What it ships

- MCP server: PagerDuty MCP server (default: `@pagerduty/mcp-server`) via `npx`.
- Skills: `page-context`.
- Hooks: `UserPromptSubmit` — detects PagerDuty incident URLs / IDs in the prompt.
- Reference: [`references/pagerduty-tools.md`](references/pagerduty-tools.md).

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** This connector's `.mcp.json` names
> `@pagerduty/mcp-server`, which does **not** resolve on npm as of 2026-06-08,
> so `npx -y @pagerduty/mcp-server` will fail to start. PagerDuty's MCP server
> may ship as a hosted endpoint, a different package name, or a CLI subcommand —
> substitute the real command in `.mcp.json` before relying on this connector.
> This is part of why the connector is `status: experimental`. See
> [`docs/CONNECTOR-POLICY.md` §4.2](../../docs/CONNECTOR-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-paging@polymath
# You'll be prompted for pagerdutyApiKey (sensitive).
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `pager` — PagerDuty, Opsgenie, Splunk On-Call
- **Polymath value:** `page-context` skill discipline; respondToIncident wiring
- **Sunset trigger:** Demote when an official pager MCP adds a first-class incident-context skill.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
