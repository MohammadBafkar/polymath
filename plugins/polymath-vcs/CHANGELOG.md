# Changelog — polymath-vcs

<!-- markdownlint-disable MD024 -->

## [0.10.1]

### Changed

- The skills' MCP-binding paragraph now tells the agent to use the host's MCP server for the provider whenever it is in the session's tool list (under any name, including claude.ai connectors), instead of gating on the SessionStart `mcpResolution` snapshot.

## [0.10.0]

### Changed

- **No auto-registered MCP servers.** The plugin no longer ships a root `.mcp.json` (Claude Code would auto-register its servers — duplicates of the host agent's own MCPs, or idle servers that fail auth). Server definitions moved to `mcp/servers.json` as a render template: reuse the host agent's registered MCP first; render + install only on opt-in (`tools/mcp-registry.py render`). See `docs/MCP-REUSE.md`.

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs github/vcs/ci from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Version-control integration: GitHub PR/issue/CI MCP + PR-URL detect + unpushed-commits nudge (GitLab/Azure DevOps/Bitbucket in the capability vocab).

### Skills

- **diagnose-ci-failure** — Diagnose a failed GitHub Actions run — fetch logs via MCP, identify the failing step, classify (flake / real / config), propose next action.
- **open-pr** — Open a GitHub PR via the github MCP server — push current branch, draft from polymath-release:pr template, set base, add reviewers, never force-push.
- **triage-issue** — Triage an inbound GitHub issue — label, severity, area, ask for missing repro details if needed, route to the right team. GitHub issues only — not other trackers.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
