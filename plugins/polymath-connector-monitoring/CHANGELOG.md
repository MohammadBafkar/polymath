# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0]

### Added

- Observability umbrella connector with three provider adapters under
  one plugin. Skills: `dashboard-snapshot` (Grafana),
  `trace-investigate` (Honeycomb), `log-search` (Elasticsearch). Each
  provider's MCP server is optional — configure only what you use.
