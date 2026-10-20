# Changelog — polymath-vuln-scan

<!-- markdownlint-disable MD024 -->

## [0.10.0]

### Changed

- **No auto-registered MCP servers.** The plugin no longer ships a root `.mcp.json` (Claude Code would auto-register its servers — duplicates of the host agent's own MCPs, or idle servers that fail auth). Server definitions moved to `mcp/servers.json` as a render template: reuse the host agent's registered MCP first; render + install only on opt-in (`tools/mcp-registry.py render`). See `docs/MCP-REUSE.md`.

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs snyk from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Vulnerability-scanning integration: Snyk test/monitor MCP + Stop-hook warning on cached open criticals (Dependabot/GHAS in the vocab).

### Skills

- **triage-vulns** — Triage Snyk findings — classify exploitable / reachable / dev-only, propose upgrade or accept-with-justification, never auto-ignore.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
