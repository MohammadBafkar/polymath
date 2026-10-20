# polymath-chat

Incident-communications concept plugin for the Polymath marketplace — internal
team chat and external public status under the `incident_comms` capability.

## What it ships

- **Skills:** `post-incident-comms`, `post-async-update` (internal team chat),
  `post-statuspage-update` (external customer-facing status).
- **Providers:** Slack (internal), Statuspage (external) — each via a
  `bindings/<provider>/binding.json` + an `mcp/servers.json` server template
  (rendered to your host's MCP config only when you opt in; if your agent
  already has a Slack MCP registered, it is reused — nothing is auto-added).
  Teams / Discord / Mattermost are recognized `incident_comms` providers and
  can be wired the same way.
- References: [`references/slack-tools.md`](references/slack-tools.md),
  [`references/statuspage-tools.md`](references/statuspage-tools.md).

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** The Statuspage server template
> (`mcp/servers.json`) names `@statuspage/mcp-server`, which does **not**
> resolve on npm as of 2026-06-08 (Slack's official server does). If you opt in
> to installing the rendered fragment, substitute a real Statuspage MCP command
> first. If your host agent already has these MCPs registered, they are reused
> and no template is needed. See
> [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-chat@polymath \
  --config slackBotToken=<xoxb-...> \
  --config defaultIncidentChannel=incidents
```

MCP servers are not auto-registered. If your agent already has a Slack or
Statuspage MCP registered, the skills use it. Otherwise run
`python3 tools/mcp-registry.py render --plugin polymath-chat --target <your-host>`
and apply the fragment to your host's MCP config.

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `incident_comms` — Slack, Statuspage (internal team chat + external public status)
- **Polymath value:** Incident-comms + async-update templates (internal) and severity-mapped public status updates (external)
- **Sunset trigger:** Demote when an official MCP ships incident-comms + public-status templates.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
