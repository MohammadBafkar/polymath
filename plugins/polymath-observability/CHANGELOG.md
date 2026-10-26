# Changelog — polymath-observability

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `author-monitor`: monitors are created only after approval of the final JSON; SLO burn-rate monitor type; the example no longer calls a p99 threshold a burn-rate alert; metric names are confirmed, not guessed.
- `metrics-design`: histogram buckets in seconds for `_seconds` metrics; no pre-computed ratio gauges; availability SLI regex.
- `tracing-strategy-otel`: a 10% head sample hides 90% of errors from tail sampling — export 100% to the collector; trace-ID load balancing; strip baggage at trust boundaries.
- `triage-error`: real Sentry suppression mechanisms (`.sentryclirc` isn't one); removed an unrelated vuln-scan line; event payloads are untrusted.
- `dashboard-snapshot`: API snapshots store only embedded data — permalink fallback; description no longer says "public".
- `trace-investigate`: origin is the deepest erroring span; removed a leaked `bb.*` attribute prefix; current semconv names.
- `log-search`: `terminate_after` makes counts partial; `query-during-incident`: discover real metric names.

## [0.10.1]

### Changed

- The skills' MCP-binding paragraph now tells the agent to use the host's MCP server for the provider whenever it is in the session's tool list (under any name, including claude.ai connectors), instead of gating on the SessionStart `mcpResolution` snapshot. `references/datadog-tools.md` documents Datadog's hosted MCP server; `author-monitor` hands over the monitor JSON when the server is read-only.

## [0.10.0]

### Changed

- **No auto-registered MCP servers.** The plugin no longer ships a root `.mcp.json` (Claude Code would auto-register its servers — duplicates of the host agent's own MCPs, or idle servers that fail auth). Server definitions moved to `mcp/servers.json` as a render template: reuse the host agent's registered MCP first; render + install only on opt-in (`tools/mcp-registry.py render`). See `docs/MCP-REUSE.md`.

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs the provider from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Observability concept plugin: RED/USE + logging + tracing design AND Datadog/Grafana/Honeycomb/Elastic/Sentry query integration.

### Skills

- **author-monitor** — Author a Datadog monitor — query, threshold, evaluation window, no-data behavior, notification routing; pair with polymath-sre:slo-design for SLO burn-rate monitors.
- **dashboard-snapshot** — Capture a Grafana dashboard snapshot for incident timelines + postmortem evidence — public-snapshot URL, time-range pinned, variables resolved.
- **log-search** — Run a typed, time-bounded log search against Elasticsearch — refuses unbounded scans, aggregates by trace id / status / route, returns a short evidence packet.
- **logging-strategy** — Define a service's logging strategy — structured JSON, level discipline, redaction, sampling for noisy paths, cost-aware retention.
- **metrics-design** — Design service metrics using RED (services) and USE (resources) — name, type, labels, cardinality budget; the smallest set that supports the SLO.
- **query-during-incident** — Run the right Datadog queries during an incident to narrow cause — error rates, latency percentiles, deploys, recent changes — and surface them concisely.
- **trace-investigate** — Investigate a Honeycomb trace by trace.id — surface the offending span, its dependency chain, error context, and a candidate root-cause hypothesis.
- **tracing-strategy-otel** — Design an OpenTelemetry tracing strategy — sampling, attribute discipline, span hygiene, context propagation, baggage, cost-aware exporter config.
- **triage-error** — Triage a Sentry issue — group context, frequency trend, recent-deploy correlation, blast radius, suggested next action (fix / ignore / re-prioritize).

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
