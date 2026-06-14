# Changelog — polymath-observability

<!-- markdownlint-disable MD024 -->

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
