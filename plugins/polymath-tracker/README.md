# polymath-tracker

Issue-tracker connector for the Polymath marketplace. One install covers the
`issue_tracker` capability across **Jira and Linear** — supply credentials for
whichever tracker your project uses (the capability vocabulary resolves
`provider: jira` and `provider: linear` to this plugin). Mirrors the umbrella
shape of `polymath-observability`.

## What it ships

- Server templates (rendered to your host's MCP config only when you opt in;
  if your agent already has an Atlassian or Linear MCP registered, it is
  reused — nothing is auto-added): Atlassian
  (`@modelcontextprotocol/server-atlassian`) and Linear (`@linear/mcp-server`)
  via `npx`, each activating from its own credentials, which default to empty
  (`${VAR:-}`) so an unconfigured template can't break rendering — it stays
  inert until you install the fragment and set the env vars.
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

<!-- mcp-package-status -->
> ⚠️ **MCP packages not yet published.** This connector's server template
> (`mcp/servers.json`) names `@modelcontextprotocol/server-atlassian` (Jira)
> and `@linear/mcp-server`, neither of which resolves on npm as of 2026-06-08,
> so the rendered `npx -y …` fragments would fail to start. Atlassian and
> Linear both offer **hosted/remote** MCP servers (and there are community npm
> packages) rather than these names — substitute the real command before
> installing a rendered fragment. If your host agent already has these MCPs
> registered, they are reused and no template is needed. This is part of why
> it is `status: experimental`. See
> [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-tracker@polymath
# Supply the jira* keys if you use Jira, or linearApiKey if you use Linear.
# All four are optional; configure the set for your tracker.
```

MCP servers are not auto-registered. If your agent already has an Atlassian
(Jira) or Linear MCP registered, the skills use it. Otherwise run
`python3 tools/mcp-registry.py render --plugin polymath-tracker --target <your-host>`
and apply the fragment for the tracker you use to your host's MCP config.

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `issue_tracker` — Jira, Linear, GitHub Issues, Azure Boards
- **Polymath value:** Triage workflows + provider-agnostic file-bug-from-incident
- **Sunset trigger:** Demote a provider if its official MCP ships triage automation covering our flow.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
