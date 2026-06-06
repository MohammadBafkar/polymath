# polymath-connector-tracker

Issue-tracker connector for the Polymath marketplace. One install covers the
`issue_tracker` capability across **Jira and Linear** — supply credentials for
whichever tracker your project uses (the capability vocabulary resolves
`provider: jira` and `provider: linear` to this plugin). Mirrors the umbrella
shape of `polymath-connector-observability`.

## What it ships

- MCP servers: Atlassian (`@modelcontextprotocol/server-atlassian`) and Linear
  (`@linear/mcp-server`) via `npx`. Each activates from its own credentials; an
  unconfigured server is simply unused.
- Skills:
  - `jira-triage` — triage an inbound Jira issue.
  - `linear-triage` — triage an inbound Linear issue.
  - `file-bug-from-incident` — provider-agnostic; files tracker tickets from a
    postmortem's action items, resolving Jira vs Linear from the configured
    provider. This is the skill workflows reach via
    `${capabilities.issue_tracker.plugin}:file-bug-from-incident`.
- Hooks: `UserPromptSubmit` — two detectors: Jira keys (`PROJ-123`) /
  `*.atlassian.net/browse/...` URLs, and Linear keys (`TEAM-123`) / URLs. Each
  hints the model to fetch via the matching MCP server.
- References: [`references/jira-tools.md`](references/jira-tools.md),
  [`references/linear-tools.md`](references/linear-tools.md).

## Installation

```bash
claude plugin install polymath-connector-tracker@polymath
# Supply the jira* keys if you use Jira, or linearApiKey if you use Linear.
# All four are optional; configure the set for your tracker.
```

## Dependencies

- `polymath-core`

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Wraps official Jira + Linear MCP servers
- **Polymath value:** Triage workflows + provider-agnostic file-bug-from-incident; one `issue_tracker` capability
- **Sunset trigger:** Demote a provider if its official MCP ships triage automation covering our flow.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
