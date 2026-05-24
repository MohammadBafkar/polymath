# polymath-connector-sentry

Sentry connector for the Polymath marketplace.

## What it ships

- MCP server: Sentry MCP server (default: `@sentry/mcp-server`) via `npx`.
- Skills: `triage-error`.
- Hooks: `UserPromptSubmit` — detects Sentry issue URLs in the prompt; detects short-IDs only when "Sentry" is mentioned nearby (avoids Jira-key false positives).
- Reference: [`references/sentry-tools.md`](references/sentry-tools.md).

## Installation

```bash
claude plugin install polymath-connector-sentry@polymath \
  --config sentryToken=<token> --config sentryOrg=<slug>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
