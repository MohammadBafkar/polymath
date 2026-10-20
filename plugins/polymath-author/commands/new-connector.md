---
name: new-connector
description: Generate an integration (MCP) plugin named by capability (polymath-<concept>) with mcp/servers.json template + userConfig via new-connector.sh; not a generic plugin (new-plugin).
---

# /new-connector

Scaffold a new integration plugin via `${POLYMATH_PLUGIN_ROOT}/bin/new-connector.sh <concept>` (a capability-ish name like `vcs`, `chat`, `paging` → `polymath-<concept>`). Generates the plugin.json (with `userConfig`), an `mcp/servers.json` render template (never an auto-registered `.mcp.json` — the host agent's MCP servers are the default source), `hooks/` directory, and `references/<concept>-tools.md` template. The vendored scaffolder walks up from the cwd to find the caller's marketplace root.

For a new *vendor* of a capability that already has a concept plugin (e.g. another `issue_tracker`), add a `bindings/<provider>/binding.json` to that plugin instead of scaffolding a new one. Integration plugins follow the standard layout (see [`docs/PLUGIN-AUTHORING.md`](../../../docs/PLUGIN-AUTHORING.md)): MCP server reference, sensitive credentials via `userConfig`, capability bindings, optional hooks, and a reference doc.
