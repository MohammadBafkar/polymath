# Elasticsearch MCP tools (reference)

Default server: `@elastic/mcp-server` (or any community Elasticsearch MCP server with the same tool shape).

Auth: `ELASTIC_API_KEY` from `userConfig`. Issue an API key scoped to the read role on specific indices; avoid superuser.

## Tools exposed (subset)

### Read

- `search` — primary query endpoint.
- `count` — fast count for sanity checks.
- `cat.indices` — index listing for pattern resolution.
- `_field_caps` — types for fields (validate field types before query).
- `_explain` — per-doc score explanation (rarely useful for ops, useful for relevance debugging).

### Write

This connector is **read-only by policy**. Index/template/mapping mutations belong with a separate ops-grade tool, not in triage.

## API key scope

Recommended scopes:

- `read` on the specific log/metric indices you triage (`logs-prod-*`, `metrics-prod-*`).
- `read_pipeline` if you query Painless-rendered fields.
- Avoid: `manage_security`, `manage_index_templates`, anything ending in `_write`.

## Common pitfalls

- `track_total_hits: true` is slow on large indices. Use `track_total_hits: 10000` for a capped count + an honest `relation` field.
- `from + size` deep paging falls over past ~10k; use `search_after` for time-ordered pagination.
- Default `size = 10` returns 10 hits even when `total = 2M`. Always set `size` explicitly.
- Numeric fields stored as `keyword` (text) cannot use range queries; check field caps before assuming `gte`/`lte` will work.
- Index name patterns are case-sensitive on most setups. `Logs-Prod-*` ≠ `logs-prod-*`.
