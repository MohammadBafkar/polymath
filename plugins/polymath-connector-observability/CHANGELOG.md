# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed from `polymath-connector-monitoring` and merged
  `polymath-connector-datadog` in, so the `observability` capability resolves to
  one plugin across all four providers (Datadog, Grafana, Honeycomb, Elastic).
  Added `query-during-incident` and `author-monitor` skills + the Datadog MCP
  server (`datadog*` userConfig keys, all optional) and `datadog-tools.md`
  reference. The capability vocabulary now maps `datadog`, `honeycomb`,
  `grafana`, and `elastic` → `polymath-connector-observability`. This also
  closes a latent gap: workflows that resolve
  `${capabilities.observability.plugin}:query-during-incident` for a
  Grafana/Honeycomb/Elastic provider now reach a real skill.

## [0.1.0]

### Added

- Observability umbrella connector with three provider adapters under
  one plugin. Skills: `dashboard-snapshot` (Grafana),
  `trace-investigate` (Honeycomb), `log-search` (Elasticsearch). Each
  provider's MCP server is optional — configure only what you use.
