# Datadog MCP tools (reference)

Default server: `@datadog/mcp-server` (or any community server speaking the same tool shape).

Auth: `DD_API_KEY` + `DD_APP_KEY` + `DD_SITE` from `userConfig`.

## Tools exposed (subset)

### Read

- `query_metrics` — Datadog metric query (`avg:metric{tag} by {dim}`).
- `query_logs` — log search.
- `query_events` — events stream (deploys, alerts, config changes).
- `list_dashboards` — dashboard catalog.
- `get_dashboard` — dashboard definition.
- `list_monitors` — monitors with filters.
- `get_monitor` — single monitor.

### Write

- `create_monitor` — author one.
- `update_monitor` — edit threshold / message / tags.
- `delete_monitor` — remove (require confirmation for prod).
- `mute_monitor` — silence with a timed expiration.

## Key scopes

Datadog API key + Application key together control access. Limit damage:

- Use a service-account application key, not a user's personal key.
- Scope app keys to the minimum role (Read-only API access for triage; Datadog Admin for write).
- Rotate at a regular cadence; the `userConfig.sensitive: true` channel scopes the key to the plugin.

## Common pitfalls

- Querying without a baseline-comparison time window — you'll mistake a healthy spike for an incident.
- Anomaly-detection monitors on metrics with too little history.
- Mute-all during deploys without a documented un-mute time.
