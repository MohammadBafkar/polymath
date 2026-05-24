# LaunchDarkly MCP tools (reference)

Default server: `@launchdarkly/mcp-server` (or any community LaunchDarkly MCP server with the same tool shape).

Auth: `LAUNCHDARKLY_API_TOKEN` from `userConfig`. Use a service token, not a personal one — service tokens survive employee turnover and carry an explicit role scope.

## Tools exposed (subset)

### Read

- `flags.list` / `flags.get` — fetch flag metadata and targeting rules; filter by project, environment, tag, archived.
- `flags.evaluations` — historical evaluation counts per variation (proxy for actual exposure).
- `projects.list` / `environments.list` — discover project + environment keys.
- `segments.list` / `segments.get` — read targeting segments.
- `audit.list` — recent flag changes (who flipped what, when).

### Write

- `flags.create` — new flag with default rule + variations.
- `flags.update` — change default rule, targeting rules, prerequisite flags, archived state.
- `flags.update-targeting` — bulk-edit a flag's user/segment targets and percentage rollouts.
- `comments.create` — attach a note to a flag (audit trail).

## Token scope

LaunchDarkly tokens are scoped via custom roles. Recommended scopes for Polymath use:

- Triage / read-only: `reader` role over `proj/<your-project>:env/*`.
- Rollout updates: `writer` role over `proj/<your-project>:env/*` excluding `production` for safety; bump to production-writer only when intentionally ramping prod.
- Avoid `admin` — it includes account-management scopes you do not need.

## Common pitfalls

- `flags.update` requires the **environment key** (e.g. `production`), not the environment name. Resolve via `environments.list`.
- Targeting changes are environment-scoped; "flip in staging" does not flip in prod.
- LaunchDarkly does not have a native retirement field — track the retirement date in the flag's description or maintenance tag and audit it externally.
- Archived flags still evaluate to their last-served variation; "archived" is metadata, not a kill switch. Use `flags.update` to set the default and clear targeting before archiving.
