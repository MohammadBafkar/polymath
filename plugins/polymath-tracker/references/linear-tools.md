# Linear MCP tools (reference)

Default server: `@linear/mcp-server` (or any community Linear MCP server with the same tool shape).

Auth: `LINEAR_API_KEY` from `userConfig`. Personal keys act as the user; prefer a service-account-style key where the workspace supports it.

## Tools exposed (subset)

### Read

- `issue.get` / `issue.list` — fetch issues; filter by team, state, label, assignee, cycle.
- `team.list` / `team.get` — resolve team identifier.
- `workflowState.list` — resolve workflow state name → ID per team (Linear needs IDs for transitions).
- `cycle.get` / `cycle.list` — sprint analog.
- `user.list` / `user.get` — resolve assignee.

### Write

- `issue.create` — new issue.
- `issue.update` — labels, priority, state, assignee, cycle.
- `comment.create` — append a comment.
- `issueRelation.create` — link issues (duplicate of, blocks, related to).

## API-key scope

Linear personal API keys have full account access. Reduce blast radius by:

- Using a dedicated bot-style user where the workspace allows it.
- Rotating quarterly.
- Never reusing the same key across multiple Polymath connectors or unrelated services.

## Common pitfalls

- Linear's `issue.update` needs **state IDs**, not state names. Resolve via `workflowState.list` first.
- Cycle assignment is by ID, not name (cycles are auto-numbered per team).
- Linear's "Cancelled" state is the right close for duplicates; "Done" is for actually-shipped work.
- Linear assigns to people, not groups. Team ownership is conveyed via labels + the team-scoped namespace.
