# polymath-connector-launchdarkly

LaunchDarkly connector for the Polymath marketplace. Wraps the LaunchDarkly MCP server with flag-rollout planning baked in.

## What it ships

- MCP server: LaunchDarkly MCP server (default: `@launchdarkly/mcp-server`) via `npx`.
- Skills: `flag-rollout-plan` — plans a flag's lifecycle from internal dogfood → ramp → retirement before any code lands behind it.
- Reference: [`references/launchdarkly-tools.md`](references/launchdarkly-tools.md).

## Installation

```bash
claude plugin install polymath-connector-launchdarkly@polymath \
  --config launchdarklyApiKey=<token> \
  --config launchdarklyProject=<project-key>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
