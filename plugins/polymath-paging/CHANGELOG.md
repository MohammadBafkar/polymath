# Changelog — polymath-paging

<!-- markdownlint-disable MD024 -->

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs pagerduty from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

On-call/paging integration: PagerDuty incident + on-call MCP + incident-URL detection (Opsgenie/Splunk On-Call in the capability vocab).

### Skills

- **page-context** — Fetch the full context for an active PagerDuty incident — log entries, oncall, related services, recent deploys — before responders join.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
