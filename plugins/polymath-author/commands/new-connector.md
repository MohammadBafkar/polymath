---
name: new-connector
description: Scaffold a polymath-connector-<service> plugin with .mcp.json and userConfig via new-connector.sh. Not a generic plugin (new-plugin).
---

# /new-connector

Scaffold a new connector via `${CLAUDE_PLUGIN_ROOT}/bin/new-connector.sh <service>`. Generates the plugin.json (with `userConfig`), `.mcp.json` stub, `hooks/` directory, and `references/<service>-tools.md` template. The vendored scaffolder walks up from the cwd to find the caller's marketplace root.

Connectors must follow the standard connector layout (see [`docs/PLUGIN-AUTHORING.md`](../../../docs/PLUGIN-AUTHORING.md)): MCP server reference, sensitive credentials via `userConfig`, optional hooks for event-driven reactions, and a reference doc.
