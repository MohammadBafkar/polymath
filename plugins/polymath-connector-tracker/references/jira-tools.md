# Jira / Atlassian MCP tools (reference)

This connector ships an `.mcp.json` that runs the Atlassian MCP server (e.g. `@modelcontextprotocol/server-atlassian`) via `npx`. Swap the `command`+`args` if you use a different community server (`mcp-atlassian`, etc.) — the rest of the connector (hooks, skills) doesn't depend on the exact server.

The token + email + URL are injected from `userConfig.jiraApiToken / jiraEmail / jiraUrl` and exposed as `ATLASSIAN_API_TOKEN` / `ATLASSIAN_EMAIL` / `ATLASSIAN_URL`.

## Tools exposed (subject to upstream server)

### Read

- `jira_get_issue` — single issue by key.
- `jira_search` — JQL.
- `jira_get_transitions` — available state transitions for an issue.
- `jira_get_project` — project metadata.
- `jira_list_issue_types` / `jira_list_priorities` — for safe defaults.

### Write

- `jira_create_issue` — new ticket.
- `jira_update_issue` — labels, priority, assignee, component, fields.
- `jira_transition_issue` — move between states.
- `jira_add_comment` — append a comment.
- `jira_link_issues` — block/clone/duplicate links.

## Token scopes

API tokens at `id.atlassian.com` are tied to the account, not a scope. Limit damage by:

- Using a dedicated service account with project-scoped permissions.
- Never granting the bot account admin permissions on any project.
- Rotating the token at a regular cadence; the `userConfig.sensitive: true` channel makes rotation a `claude plugin install` re-run.

## Common pitfalls

- Some Jira instances disable JQL `parent` queries for non-admins — fall back to `parent in (X)` only when permitted.
- `jira_transition_issue` requires the **transition ID**, not the target state name. Call `jira_get_transitions` first.
- Custom fields are referenced by `customfield_NNNNN` — fetch the project's field map once and cache it.
