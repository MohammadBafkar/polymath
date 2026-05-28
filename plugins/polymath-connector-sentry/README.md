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

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Sentry MCP
- **Polymath value:** `triage-error` shape: group context + recent-deploy correlation
- **Sunset trigger:** Demote when Sentry MCP ships triage automation covering the four signals.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

Apache-2.0.
