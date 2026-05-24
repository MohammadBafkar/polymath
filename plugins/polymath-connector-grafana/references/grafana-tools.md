# Grafana MCP tools (reference)

Default server: `@grafana/mcp-server` (or any community Grafana MCP server with the same tool shape).

Auth: `GRAFANA_API_KEY` from `userConfig`. Use a **service account token**, not a personal user token.

## Tools exposed (subset)

### Read

- `dashboards.uid` / `dashboards.search` — find dashboards.
- `datasources.list` / `datasources.get`
- `folders.list`
- `query.datasource` — run an ad-hoc query against a datasource (useful when a panel's expression is the question).
- `annotations.list`

### Write

- `snapshots.create` — primary write used by this connector. Snapshots are scoped, expiring artifacts.
- `annotations.create` — drop a marker on a dashboard timeline (e.g. "deploy at 14:02"). Helpful but unrelated to snapshot capture.
- `dashboards.update` — out of scope for this connector.

## Token scope

- Viewer is enough for `query.datasource` + `dashboards.uid`.
- Editor is required for `snapshots.create` (Grafana counts snapshots as edits).
- Avoid Admin tokens.

## Common pitfalls

- Snapshot capture is a deep clone of the dashboard JSON at that moment. If the dashboard changes later, the snapshot is unaffected (good for postmortem evidence; bad if you wanted live-updating).
- Template variables embedded in the snapshot are *frozen*. Multi-value variables that were "All" at capture stay "All" forever.
- `expires=0` is "never expires" on most Grafana versions. Use a finite TTL.
- External snapshots (`snapshots.raintank.io` or your configured external service) are publicly addressable; never use for sensitive labels.
- Annotations are dashboard-scoped, not org-wide; a deploy annotation on dashboard A is invisible on dashboard B.
