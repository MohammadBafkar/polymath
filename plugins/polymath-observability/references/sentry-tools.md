# Sentry MCP tools (reference)

Default server: `@sentry/mcp-server` (or any community Sentry MCP server with the same tool shape).

Auth: `SENTRY_AUTH_TOKEN` + `SENTRY_ORG` from `userConfig`.

## Tools exposed (subset)

### Read

- `get_issue` — single issue by id or short-id.
- `list_issues` — issues with filters (project, env, status, query).
- `list_events` — events in an issue.
- `get_event` — single event with full stack + breadcrumbs.
- `list_projects` — projects in the org.
- `list_releases` — recent releases for correlation.

### Write

- `update_issue` — resolve, ignore, assign.
- `set_issue_status` — status transitions.
- `add_issue_comment` — append a note.

## Token scopes (Sentry auth tokens)

For triage-only:

- `event:read`, `project:read`, `org:read`.

For write (resolve, ignore, assign):

- `event:write`, `project:write`.

Prefer per-org tokens over user tokens. Rotate when the bot account changes.

## Anti-patterns

- Auto-resolving issues from the model without a fix landing. The error reappears; users see the regression twice.
- Ignoring without a `.sentryclirc` suppression rule (or equivalent project-level Sentry ignore). Repeats next triage pass.
- Treating "user count" as the universal impact metric. Low-user / high-value paths (payment, account recovery) outweigh high-user / low-value (marketing pageviews).
