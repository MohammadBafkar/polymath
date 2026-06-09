# polymath-connector-observability

Observability umbrella connector for the Polymath marketplace —
merges Datadog + Grafana + Honeycomb + Elasticsearch under one plugin so a user
can install one capability and configure only the providers they
actually use.

## What it ships

- **Skills:**
  - `dashboard-snapshot` — capture a permalinked Grafana dashboard
    snapshot for incident timelines and postmortem evidence.
  - `trace-investigate` — walk a Honeycomb trace, surface the
    offending span with its dependency chain.
  - `log-search` — Elasticsearch time-bounded, field-typed queries
    that refuse unbounded scans.
  - `query-during-incident` — focused Datadog metric/log queries that
    narrow root cause under incident time pressure.
  - `author-monitor` — author a Datadog monitor with sane thresholds,
    burn-rate windows, and notification routing.
- **References:** `datadog-tools.md`, `grafana-tools.md`,
  `honeycomb-tools.md`, `elastic-tools.md` — provider MCP tool catalogs.
- **MCP servers:** all four are declared in `.mcp.json`. Configure only the
  providers your project uses; the others' credentials default to empty
  (`${VAR:-}`) so an unconfigured provider can't break MCP config parsing — its
  server starts idle and fails its own auth rather than blocking the session. To
  avoid the idle servers entirely, disable the unused ones via the `/mcp` UI.

Datadog (`query-during-incident`, `author-monitor`) was folded in from the
former `polymath-connector-datadog`, so the `observability` capability resolves
to one plugin across all four providers.

## Pairs with

- `polymath-observability` — RED/USE metrics design, logging
  strategy, tracing strategy. Use those skills to design what you
  emit; use this plugin to investigate what you've emitted.
- `polymath-sre:slo-design` — SLO burn-rate queries land in
  Grafana / Honeycomb.
- `polymath-incident:postmortem-blameless` — snapshots become
  postmortem evidence.

<!-- mcp-package-status -->
> ⚠️ **MCP packages not yet published.** This connector's `.mcp.json` names
> `@datadog/mcp-server`, `@grafana/mcp-server`, `@honeycomb/mcp-server`, and
> `@elastic/mcp-server` — **none** resolve on npm as of 2026-06-08, so the
> `npx -y …` commands will fail to start. Each vendor distributes its MCP server
> differently (hosted endpoint, Go binary, or a different package) — substitute
> the real command(s) in `.mcp.json` for the provider(s) you use before relying
> on this connector. This is part of why it is `status: experimental`. See
> [`docs/CONNECTOR-POLICY.md` §4.2](../../docs/CONNECTOR-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-connector-observability@polymath
```

Then configure only the providers you actually use — the others'
credentials can be left blank.

## v0.2 — merged from three predecessors

Three provider adapters — Grafana, Honeycomb, and Elasticsearch —
share one umbrella plugin under the `observability` capability.
Projects select the provider in `.polymath/capabilities.yaml`; skills
route to the configured adapter rather than the plugin namespace.

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps Datadog + Grafana + Honeycomb + Elasticsearch MCPs under one observability capability
- **Polymath value:** Snapshot + trace-walk + bounded-scan + incident-query + monitor-authoring disciplines; single capability mapping for all four
- **Sunset trigger:** Demote a provider when its upstream MCP ships postmortem-evidence + investigative templates.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
