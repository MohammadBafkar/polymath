# Honeycomb MCP tools (reference)

Default server: `@honeycomb/mcp-server` (or any community Honeycomb MCP server with the same tool shape).

Auth: `HONEYCOMB_API_KEY` from `userConfig`. Use an **environment-scoped** key; classic ingest keys are for ingestion only.

## Tools exposed (subset)

### Read

- `queries.run` — primary query endpoint (calculations, breakdowns, filters, order, limit).
- `triggers.list` — saved triggers (alerts).
- `boards.list` — saved boards (dashboards).
- `markers.list` — deploy markers / annotations on a dataset's timeline.
- `datasets.list`

### Write

- `markers.create` — drop a marker on a dataset (e.g. "deploy at 14:02"). Used by `polymath-release` workflows, not by this skill.

## API key scope

- Environment keys cover one environment + dataset namespace; preferred for triage.
- Ingestion keys (classic) only allow write; cannot query.
- Avoid superuser keys; they cross environment boundaries.

## Common pitfalls

- Honeycomb queries are dataset-scoped. Cross-dataset analysis requires multiple queries. Trace IDs span datasets but `queries.run` does not.
- `BREAKDOWN trace.span_id` returns one row per span — pair with `WHERE trace.id = <id>` to scope to one trace.
- Span ordering by `start_time` is NOT the same as causal ordering. Walk `trace.parent_id` to reconstruct the tree.
- `error = true` is a convention, not a guarantee — some instrumentations set `status_code != OK` instead. Filter for both.
- Self-time = `duration_ms` - sum(child `duration_ms`). Honeycomb does not pre-compute self-time; the skill must calculate it.
