# Changelog — polymath-chat

<!-- markdownlint-disable MD024 -->

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs slack from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Incident-comms integration: Slack channels/threads + Statuspage public updates — internal + external incident communication.

### Skills

- **post-async-update** — Post an async standup / status update to a Slack channel — short, structured (yesterday / today / blockers), threaded under a daily anchor.
- **post-incident-comms** — Post an incident-comms update to the right Slack channel + thread; pairs with polymath-incident:comms-update for the body and respondToIncident for context.
- **post-statuspage-update** — Post a customer-facing Statuspage incident update — maps internal severity to public status, scopes components, and re-writes the comms body for customers.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
