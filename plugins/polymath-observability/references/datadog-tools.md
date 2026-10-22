# Datadog MCP tools (reference)

Two server shapes are in use; the tool names differ. Use whichever the host has registered (see the skill's MCP binding preamble) and map each step to the closest tool.

- **Self-run `@datadog/mcp-server`** (or a community server with the same shape): tools below. Auth: `DD_API_KEY` + `DD_APP_KEY` + `DD_SITE`.
- **Datadog's hosted MCP server**, often added as a claude.ai connector or by URL (`https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`, other sites on their own host): OAuth, no keys in the repo. Read tools are named `search_datadog_*` / `get_datadog_*` (see [Hosted server](#hosted-server-tools)). It may be **read-only** — OAuth grants without MCP write access omit the write tools.

## Hosted server tools

Names as the server defines them; the host adds its own prefix (`mcp__claude_ai_Datadog__` for a claude.ai connector).

| Step | Tool |
| --- | --- |
| Logs | `search_datadog_logs`, `analyze_datadog_logs` |
| Metrics | `get_datadog_metric`, `search_datadog_metrics`, `get_datadog_metric_context` |
| Traces / spans | `search_datadog_spans`, `get_datadog_trace`, `aggregate_spans` |
| Events (deploys, alerts, changes) | `search_datadog_events`, `aggregate_events` |
| Monitors | `search_datadog_monitors`, `validate_monitor_definition`, `recommend_monitor_threshold` |
| Dashboards | `search_datadog_dashboards`, `get_datadog_dashboard` |
| Incidents / errors | `search_datadog_incidents`, `search_datadog_error_tracking_issues` |

Monitor **creation is not available** on a read-only server: produce the monitor JSON, run `validate_monitor_definition` on it when offered, and hand the user the payload to apply.

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
