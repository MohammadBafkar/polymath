# Statuspage MCP tools (reference)

Default server: `@statuspage/mcp-server` (or any community Statuspage MCP server with the same tool shape).

Auth: `STATUSPAGE_API_KEY` + `STATUSPAGE_PAGE_ID` from `userConfig`. Keys are scoped per Statuspage page — never reuse a key across multiple pages.

## Tools exposed (subset)

### Read

- `pages.get` — fetch the page configuration (mostly for sanity-check on startup).
- `components.list` / `components.get` — resolve public component name → ID. Required before any incident update referencing components.
- `incidents.list` — open + recent incidents (filter by `status`).
- `incidents.get` — one incident with its update history.

### Write

- `incidents.create` — new incident with status (`investigating`/`identified`/etc.), impact (`critical`/`major`/`minor`/`none`), body, affected component IDs.
- `incidents.update` — post a new update on an existing incident (status, body, impact, component state changes).
- `incidents.resolve` — convenience for the terminal update; sets `status = resolved` and flips components to `operational` if you pass `update_component_statuses=true`.
- `components.update` — change a component's status without an incident (rare; avoid using this to "fix" a stuck component state — post a real incident update instead).

## API-key scope

Statuspage page-scoped keys carry full write access on that page. Reduce blast radius by:

- One key per page (a single org with prod + staging pages should issue two keys).
- Rotating after each `polymath-incident:postmortem` confirms an incident is closed for ≥ 7 days.
- Never embedding keys in workflow snapshots — Polymath stores via `userConfig.sensitive: true`.

## Common pitfalls

- `incidents.update` accepts `component_ids` as **IDs**, not component names. Always go through `components.list` first.
- The `status` field has a strict state machine: `investigating` → `identified` → `monitoring` → `resolved`. Going backwards (e.g. resolved → monitoring) requires a new incident.
- `impact` is a snapshot per update. If the impact actually changed (e.g. you over-estimated), post an update that lowers it explicitly — do not silently re-rate the past.
- Statuspage timestamps are UTC. The widget renders in the viewer's timezone, but the API consumes UTC; mixing them causes "Next update at 14:00" to land an hour off.
