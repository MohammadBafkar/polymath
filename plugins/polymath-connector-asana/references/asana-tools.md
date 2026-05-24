# Asana MCP tools (reference)

Default server: `@asana/mcp-server` (or any community Asana MCP server with the same tool shape).

Auth: `ASANA_ACCESS_TOKEN` from `userConfig`. Service-account tokens preferred; personal tokens carry full user scope.

## Tools exposed (subset)

### Read

- `tasks.get` / `tasks.list` — fetch tasks; filter by project, section, assignee, completed-since.
- `sections.list` / `sections.get` — resolve section name → GID.
- `projects.get` / `projects.list` — discover projects in a workspace.
- `custom_field_settings.list` — list custom fields available on a project (resolve names → GIDs).
- `users.list` / `users.get` — resolve assignee names/emails → user GIDs.

### Write

- `tasks.update` — change task fields; merges, does not overwrite (omit to leave unchanged).
- `tasks.create` — new task in a project (and optionally section via `memberships`).
- `sections.addTask` — move a task between sections (separate from `tasks.update`).
- `stories.create` — add a comment/story to a task.
- `tasks.addFollowers` / `removeFollowers` — change notification recipients.

## Token scope

Asana personal access tokens cover everything the user can see. Reduce blast radius by:

- Issuing a service-account user (e.g. `polymath-bot@`) and adding it only to relevant projects.
- Rotating quarterly.
- Avoiding workspace-admin members for automation tokens.

## Common pitfalls

- Asana uses **GIDs** for every reference (project, section, user, custom field, custom-field-option). Name-based references in `tasks.update` are silently ignored.
- Custom-field updates merge: passing `custom_fields: { gid: value }` updates *that* field only; you need not send the whole map.
- Moving a task between projects is a `tasks.addProject` + (optional) `sections.addTask`; `tasks.update` cannot do it.
- `completed: true` does not propagate to subtasks. Closing the parent does not close children.
- Asana's rate limit is generous but not infinite; ~150 req/min per token. Bulk renames need pacing.
