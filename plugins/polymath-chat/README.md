# polymath-chat

Slack connector for the Polymath marketplace.

## What it ships

- MCP server: `@modelcontextprotocol/server-slack` via `npx`.
- Skills: `post-incident-comms`, `post-async-update`.
- Reference: [`references/slack-tools.md`](references/slack-tools.md).

## Installation

```bash
claude plugin install polymath-chat@polymath \
  --config slackBotToken=<xoxb-...> \
  --config defaultIncidentChannel=incidents
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Slack MCP
- **Polymath value:** Incident-comms + async-update templates
- **Sunset trigger:** Demote when Slack MCP ships incident-comms templates.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
