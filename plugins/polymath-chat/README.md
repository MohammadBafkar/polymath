# polymath-chat

Incident-communications concept plugin for the Polymath marketplace — internal
team chat and external public status under the `incident_comms` capability.

## What it ships

- **Skills:** `post-incident-comms`, `post-async-update` (internal team chat),
  `post-statuspage-update` (external customer-facing status).
- **Providers:** Slack (internal), Statuspage (external) — each via a
  `bindings/<provider>/binding.json` + a `.mcp.json` server. Teams / Discord /
  Mattermost are recognized `incident_comms` providers and can be wired the
  same way.
- References: [`references/slack-tools.md`](references/slack-tools.md),
  [`references/statuspage-tools.md`](references/statuspage-tools.md).

<!-- mcp-package-status -->
> ⚠️ **MCP package not yet published.** `@statuspage/mcp-server` does **not**
> resolve on npm as of 2026-06-08 (Slack's official server does). Substitute a
> real Statuspage MCP command in `.mcp.json` before relying on it. See
> [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-chat@polymath \
  --config slackBotToken=<xoxb-...> \
  --config defaultIncidentChannel=incidents
```

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
