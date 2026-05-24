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

## License

Apache-2.0.
