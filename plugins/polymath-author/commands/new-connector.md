---
name: new-connector
description: Scaffold a new polymath-connector-<service> plugin via tools/new-connector.sh.
---

# /new-connector

Scaffold a new connector via `tools/new-connector.sh <service>`. Generates the plugin.json (with `userConfig`), `.mcp.json` stub, `hooks/` directory, and `references/<service>-tools.md` template.

Connectors must follow the standard connector layout (see [`docs/PLUGIN-AUTHORING.md`](../../../docs/PLUGIN-AUTHORING.md)): MCP server reference, sensitive credentials via `userConfig`, optional hooks for event-driven reactions, and a reference doc.
