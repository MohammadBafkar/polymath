# polymath-vcs

GitHub connector for the Polymath marketplace.

## What it ships

- MCP server template: `@modelcontextprotocol/server-github` (via `npx`) —
  rendered to your host's MCP config only when you opt in; if your agent
  already has a GitHub MCP registered, it is reused.
- Skills: `open-pr`, `triage-issue`, `diagnose-ci-failure`.
- Hooks:
  - `UserPromptSubmit` — detects PR URLs in the prompt and hints the model to fetch via the MCP server.
  - `Stop` — quietly nudges to open a PR when the branch has unpushed commits.
- Reference: [`references/github-tools.md`](references/github-tools.md) — what the MCP exposes + PAT scope guidance.

## Installation

```bash
claude plugin install polymath-vcs@polymath
# You'll be prompted for githubToken (sensitive).
```

MCP servers are not auto-registered. If your agent already has a GitHub MCP
registered, the skills use it. Otherwise run
`python3 tools/mcp-registry.py render --plugin polymath-vcs --target <your-host>`
and apply the fragment to your host's MCP config.

## Token

Fine-grained PAT recommended. Required scopes documented in [`references/github-tools.md`](references/github-tools.md).

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `vcs` (+ `ci`) — GitHub, GitLab, Azure DevOps, Bitbucket
- **Polymath value:** Triage + PR-open workflow shape; CI-failure diagnosis on Stop; provider-agnostic across forges
- **Sunset trigger:** Demote a provider when its official MCP grows opinionated triage + CI diagnosis.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
