# polymath-connector-github-actions

GitHub Actions companion for `polymath-connector-github`. Adds CI-specific hooks and skills on top of the shared MCP server.

## What it ships

- Skills: `diagnose-ci-failure`.
- Hooks: `Stop` — if the latest Actions run on the current branch failed, hint at log fetch / re-run via the github MCP.
- Reference: [`references/github-actions-tools.md`](references/github-actions-tools.md).

## Installation

```bash
claude plugin install polymath-connector-github-actions@polymath
# Requires polymath-connector-github (auto-installed via dependency).
```

## Dependencies

- `polymath-core`
- `polymath-connector-github` (provides the MCP server + token)

## License

Apache-2.0.
