# polymath-connector-jira

Jira connector for the Polymath marketplace.

## What it ships

- MCP server: Atlassian MCP server (default: `@modelcontextprotocol/server-atlassian`) via `npx`.
- Skills: `jira-triage`, `file-bug-from-incident`.
- Hooks: `UserPromptSubmit` — detects Jira keys (`PROJ-123`) and `https://*.atlassian.net/browse/...` URLs in the prompt; hints the model to fetch via the MCP.
- Reference: [`references/jira-tools.md`](references/jira-tools.md).

## Installation

```bash
claude plugin install polymath-connector-jira@polymath
# You'll be prompted for jiraUrl, jiraEmail, and jiraApiToken (sensitive).
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Jira MCP
- **Polymath value:** Triage workflow + file-bug-from-incident shape
- **Sunset trigger:** Demote if Jira MCP ships triage automation covering our flow.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
