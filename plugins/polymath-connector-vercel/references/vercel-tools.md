# Vercel MCP tools (reference)

Default server: `@vercel/mcp-server` (or any community Vercel MCP server with the same tool shape).

Auth: `VERCEL_ACCESS_TOKEN` from `userConfig`. Team-scoped tokens preferred.

## Tools exposed (subset)

### Read

- `deployments.get` / `deployments.list`
- `deployments.logs.builds` — build step logs.
- `deployments.logs.runtime` — runtime logs (paginated; recent N minutes).
- `deployments.aliases.list` — which domains point at this deployment.
- `projects.get` / `projects.list`
- `domains.list` — domain assignments per project.
- `events.list` — team-level audit events.

### Write (operator-approval territory)

- `deployments.promote` — promote a preview to production.
- `deployments.delete` — delete a deployment (rare; usually `cancel` is enough).
- `aliases.create` — point an alias at a deployment.

## Token scope

Vercel team tokens carry team-wide write access by default. Reduce blast radius by:

- Issuing dedicated tokens per use case (read-only inspector vs. CI deploys).
- Using SCIM/SAML-bound users for team membership where the team plan supports it.
- Rotating quarterly.

## Common pitfalls

- `state=READY` only indicates the build succeeded; runtime regressions need separate verification via `logs.runtime`.
- Vercel runtime logs are not infinite; older entries fall off. For long-lived analysis, ship logs to a log-management vendor.
- Aliases are not deployments. Promoting a deployment also rewires aliases; rolling back means re-promoting an older deployment, not editing aliases directly.
- Edge functions report `exit_code` in the runtime log; non-zero indicates runtime failure even if the deployment shows healthy.
- `deployments.list` is paginated by `updatedAt`; rollback targets need an explicit `target=production&state=READY` filter or the previous *preview* slips in.
