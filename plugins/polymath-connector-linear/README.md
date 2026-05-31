# polymath-connector-linear

Linear connector for the Polymath marketplace. Alternative to `polymath-connector-jira` for teams on Linear.

## What it ships

- MCP server: Linear MCP server (default: `@linear/mcp-server`) via `npx`.
- Skills: `linear-triage`, `file-bug-from-incident`.
- Hooks: `UserPromptSubmit` — detects `linear.app/.../issue/TEAM-NN` URLs, and `TEAM-NN` keys when "Linear" is mentioned in the prompt (vendor-ID + Jira-key disambiguation).
- Reference: [`references/linear-tools.md`](references/linear-tools.md).

## Installation

```bash
claude plugin install polymath-connector-linear@polymath --config linearApiKey=<key>
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Linear MCP
- **Polymath value:** Triage workflow shape parallel to Jira
- **Sunset trigger:** Same trigger as Jira connector.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
