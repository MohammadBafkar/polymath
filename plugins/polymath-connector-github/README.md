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

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official GitHub MCP (incl. GitHub Actions diagnostics)
- **Polymath value:** Triage + PR-open workflow shape; CI-failure diagnosis on Stop
- **Sunset trigger:** Demote when GitHub MCP grows opinionated triage flow + CI diagnosis.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

Apache-2.0.
