# Changelog — polymath-vuln-scan

<!-- markdownlint-disable MD024 -->

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs snyk from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Vulnerability-scanning integration: Snyk test/monitor MCP + Stop-hook warning on cached open criticals (Dependabot/GHAS in the vocab).

### Skills

- **triage-vulns** — Triage Snyk findings — classify exploitable / reachable / dev-only, propose upgrade or accept-with-justification, never auto-ignore.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
