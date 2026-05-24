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

## License

Apache-2.0.
