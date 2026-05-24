# polymath-connector-asana

Asana connector for the Polymath marketplace. Alternative to `polymath-connector-jira` / `polymath-connector-linear` for teams on Asana.

## What it ships

- MCP server: Asana MCP server (default: `@asana/mcp-server`) via `npx`.
- Skills: `asana-task-update` — Asana's GID-everywhere model handled correctly (sections, assignees, custom fields, enum options all resolved to GIDs).
- Reference: [`references/asana-tools.md`](references/asana-tools.md).

## Installation

```bash
claude plugin install polymath-connector-asana@polymath \
  --config asanaToken=<token> \
  --config asanaWorkspaceId=<gid>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
