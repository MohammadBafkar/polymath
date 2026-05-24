# polymath-connector-honeycomb

Honeycomb connector for the Polymath marketplace. Trace-by-trace investigation with offending-span detection and self-time latency breakdown.

## What it ships

- MCP server: Honeycomb MCP server (default: `@honeycomb/mcp-server`) via `npx`.
- Skills: `trace-investigate` — span tree + offending-span by ancestor walk + self-time latency + hypothesis with cited evidence.
- Reference: [`references/honeycomb-tools.md`](references/honeycomb-tools.md).

## Installation

```bash
claude plugin install polymath-connector-honeycomb@polymath \
  --config honeycombApiKey=<key> \
  --config honeycombDataset=refund-api
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
