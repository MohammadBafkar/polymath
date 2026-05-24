# polymath-connector-github

GitHub connector for the Polymath marketplace.

## What it ships

- MCP server: `@modelcontextprotocol/server-github` (via `npx`).
- Skills: `open-pr`, `triage-issue`.
- Hooks:
  - `UserPromptSubmit` — detects PR URLs in the prompt and hints the model to fetch via the MCP server.
  - `Stop` — quietly nudges to open a PR when the branch has unpushed commits.
- Reference: [`references/github-tools.md`](references/github-tools.md) — what the MCP exposes + PAT scope guidance.

## Installation

```bash
claude plugin install polymath-connector-github@polymath
# You'll be prompted for githubToken (sensitive).
```

## Token

Fine-grained PAT recommended. Required scopes documented in [`references/github-tools.md`](references/github-tools.md).

## Dependencies

- `polymath-core`

## License

Apache-2.0.
