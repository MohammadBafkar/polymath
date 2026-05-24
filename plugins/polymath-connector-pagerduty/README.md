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

## License

Apache-2.0.
