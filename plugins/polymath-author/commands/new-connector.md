---
name: new-connector
description: Scaffold an integration (MCP) plugin named by capability (polymath-<concept>) with .mcp.json + userConfig via new-connector.sh. Not a generic plugin (new-plugin).
---

# /new-connector

Scaffold a new integration plugin via `${CLAUDE_PLUGIN_ROOT}/bin/new-connector.sh <concept>` (a capability-ish name like `vcs`, `chat`, `paging` → `polymath-<concept>`). Generates the plugin.json (with `userConfig`), `.mcp.json` stub, `hooks/` directory, and `references/<concept>-tools.md` template. The vendored scaffolder walks up from the cwd to find the caller's marketplace root.

For a new *vendor* of a capability that already has a concept plugin (e.g. another `issue_tracker`), add a `bindings/<provider>/binding.json` to that plugin instead of scaffolding a new one. Integration plugins follow the standard layout (see [`docs/PLUGIN-AUTHORING.md`](../../../docs/PLUGIN-AUTHORING.md)): MCP server reference, sensitive credentials via `userConfig`, capability bindings, optional hooks, and a reference doc.
