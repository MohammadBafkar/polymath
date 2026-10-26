# Changelog — polymath-tracker

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Changed

- `file-bug-from-incident`: provider resolved from capabilities + the session's tool list (not credential names); re-runs skip already-filed tickets; non-bug actions filed as tasks; never guesses an assignee or a due date.
- `jira-triage`, `linear-triage`: ticket text is untrusted; field updates and comments are confirmed before writing.

## [0.10.1]

### Changed

- The skills' MCP-binding paragraph now tells the agent to use the host's MCP server for the provider whenever it is in the session's tool list (under any name, including claude.ai connectors), instead of gating on the SessionStart `mcpResolution` snapshot.

## [0.10.0]

### Changed

- **No auto-registered MCP servers.** The plugin no longer ships a root `.mcp.json` (Claude Code would auto-register its servers — duplicates of the host agent's own MCPs, or idle servers that fail auth). Server definitions moved to `mcp/servers.json` as a render template: reuse the host agent's registered MCP first; render + install only on opt-in (`tools/mcp-registry.py render`). See `docs/MCP-REUSE.md`.

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs jira/linear from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Issue-tracker connector: Jira + Linear MCP + ticket-key detection (PROJ-123 / TEAM-123 / browse URLs); triage + provider-agnostic file-bug-from-incident.

### Skills

- **file-bug-from-incident** — File tracker bug tickets from a postmortem's action items — one per action, severity/priority mapped from incident sev, postmortem updated with the keys. Provider-agnostic (Jira or Linear).
- **jira-triage** — Triage a Jira issue — fetch via MCP, classify type/priority/component, ask for missing repro, transition state, route owner. Jira only — not other trackers.
- **linear-triage** — Triage a Linear issue — classify type/priority/state, ask for missing repro, transition through the workflow state machine, route to the right team. Linear only — not other trackers.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
