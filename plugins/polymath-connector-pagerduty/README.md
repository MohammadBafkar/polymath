# polymath-connector-pagerduty

PagerDuty connector for the Polymath marketplace.

## What it ships

- MCP server: PagerDuty MCP server (default: `@pagerduty/mcp-server`) via `npx`.
- Skills: `page-context`.
- Hooks: `UserPromptSubmit` — detects PagerDuty incident URLs / IDs in the prompt.
- Reference: [`references/pagerduty-tools.md`](references/pagerduty-tools.md).

## Installation

```bash
claude plugin install polymath-connector-pagerduty@polymath
# You'll be prompted for pagerdutyApiKey (sensitive).
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official PagerDuty MCP
- **Polymath value:** `page-context` skill discipline; respondToIncident wiring
- **Sunset trigger:** Demote when PagerDuty MCP adds first-class incident-context skill.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
