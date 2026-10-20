# polymath-paging

PagerDuty connector for the Polymath marketplace.

## What it ships

- MCP server template: PagerDuty MCP server (default: `@pagerduty/mcp-server`)
  — rendered to your host's MCP config only when you opt in; if your agent
  already has a PagerDuty MCP registered, it is reused.
- Skills: `page-context`.
- Hooks: `UserPromptSubmit` — detects PagerDuty incident URLs / IDs in the prompt.
- Reference: [`references/pagerduty-tools.md`](references/pagerduty-tools.md).

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** This connector's server template
> (`mcp/servers.json`) names `@pagerduty/mcp-server`, which does **not**
> resolve on npm as of 2026-06-08, so the rendered `npx -y @pagerduty/mcp-server`
> fragment would fail to start. PagerDuty's MCP server may ship as a hosted
> endpoint, a different package name, or a CLI subcommand — substitute the real
> command before installing a rendered fragment. If your host agent already has
> a PagerDuty MCP registered, it is reused and no template is needed. This is
> part of why the connector is `status: experimental`. See
> [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-paging@polymath
# You'll be prompted for pagerdutyApiKey (sensitive).
```

MCP servers are not auto-registered. If your agent already has a PagerDuty MCP
registered, the skills use it. Otherwise run
`python3 tools/mcp-registry.py render --plugin polymath-paging --target <your-host>`
and apply the fragment to your host's MCP config.

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `pager` — PagerDuty, Opsgenie, Splunk On-Call
- **Polymath value:** `page-context` skill discipline; respondToIncident wiring
- **Sunset trigger:** Demote when an official pager MCP adds a first-class incident-context skill.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
