# polymath-connector-figma

Figma connector for the Polymath marketplace. Turns Figma frames into engineer-ready specs.

## What it ships

- MCP server: Figma MCP server (default: `@figma/mcp-server`) via `npx`.
- Skills: `design-spec-handoff` — component instances + design tokens + designed-vs-missing states + verbatim copy + a11y crosscheck.
- Reference: [`references/figma-tools.md`](references/figma-tools.md).

## Installation

```bash
claude plugin install polymath-connector-figma@polymath --config figmaAccessToken=<token>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
