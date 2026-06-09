# Connector and infra plugin policy

This document governs every **integration** plugin (one that ships a
`.mcp.json` or capability `bindings/` — e.g. `polymath-vcs`, `polymath-chat`,
`polymath-observability`) and every **infra** plugin (`polymath-cloud`,
`polymath-kubernetes`). It exists because the most common criticism of any
plugin catalog is that such plugins duplicate official MCPs, official docs, or
vendor tooling without adding distinct value.

The policy:

> Official MCPs, official docs, official LSPs, and vendor tools own
> factual and tooling behaviour. Polymath owns workflow shape,
> critique, safety opinions, and artifact discipline. A Polymath
> connector or infra plugin is only justified when it adds something
> the official surface does not already give the user.

For language depth (.NET, Python, Laravel, …) Polymath defers
entirely to specialist external catalogs (e.g.
[dotnet/skills](https://github.com/dotnet/skills),
[Laravel Boost](https://laravel.com/docs/12.x/boost),
[agentskills.io](https://agentskills.io)). Projects declare the
external catalogs they recommend in `.polymath/project.yaml`
`external_skills:` (see
[`docs/PROJECT-LOCALIZATION.md`](PROJECT-LOCALIZATION.md)).

Every plugin in scope must declare, in its `README.md`, the four
fields below. The same four fields are mirrored here for audit.

## 1. Required disclosure

```yaml
official_surface:
  exists: true | false
  source: <URL — official MCP server, vendor doc, or LSP>
polymath_value:
  - <one line per distinct workflow / critique / safety addition>
sunset_clause:
  trigger: <observable event that retires this plugin>
  action: <demote to deprecated, or merge into a recipe>
status: stable | beta | experimental | deprecated
```

If `official_surface.exists == true` and `polymath_value` is empty,
the plugin is in violation of this policy and must be demoted to
`deprecated` in `.claude-plugin/marketplace.json` at the next
release.

## 2. Categories

| Category                       | Default tier   | When to promote                                                                            |
| ------------------------------ | -------------- | ------------------------------------------------------------------------------------------ |
| Wraps an official MCP          | `experimental` | Only when a Polymath workflow + golden fixture proves added safety / critique / shape.     |
| No official MCP exists yet     | `beta`         | When Polymath ships at least one workflow that uses the connector + a live golden fixture. |
| Wraps an official skill / LSP  | `experimental` | Same bar as the MCP-wrap case.                                                             |
| Pure workflow / artifact shape | `beta`         | When at least one external user beyond the maintainer has adopted it.                      |

Connector and infra plugins are **eligible for `beta` or `stable`
only after distinct-value proof plus the normal promotion gates** —
they do not "stay experimental" by policy, but the bar above
experimental is higher than for a pure skill plugin. The distinct-value
URL — primary-source evidence (a bakeoff case, side-by-side artifact,
or documented workflow-shape gap) showing Polymath adds workflow,
critique, safety, or artifact value beyond the official surface — is
recorded in
[`registry/stability-evidence.json`](../registry/stability-evidence.json)
as `distinct_value_url` and enforced by `tools/check-stability-evidence.py`
(rule `STABILITY-1`). Without it the ledger blocks the promotion.

## 3. Per-plugin audit

The table below records the disclosure for each in-scope plugin.
Empty `polymath_value` columns are flagged for demotion at the next
release.

### 3.1 Concept (integration) plugins

Named by the capability they serve; each maps multiple vendor providers under
one capability (see `registry/schemas/capabilities.json`). Providers are wired
incrementally via `bindings/<provider>/binding.json`. Each pairs **MCP-dependent
skills** (the procedure) with the `.mcp.json` server that backs them — the skill
is the recipe, the MCP is the tooling (see the `polymath-core:glossary`); such
skills are `claude-coupled` for portability (`docs/PORTABILITY.md`).

| Plugin                  | Capability / providers                                                                 | Polymath value                                                                                           | Sunset trigger                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `polymath-observability` | `observability` — Datadog, Grafana, Honeycomb, Elastic, Sentry (merged with the observability design discipline) | RED/USE + logging + tracing design **and** snapshot / trace-walk / bounded-scan / incident-query / monitor-authoring / error-triage across providers | Demote a provider when its upstream MCP ships postmortem-evidence + investigative templates. |
| `polymath-vcs`          | `vcs` (+ `ci`) — GitHub, GitLab, Azure DevOps, Bitbucket                                | Triage + PR-open workflow shape; CI-failure diagnosis on Stop; provider-agnostic across forges           | Demote a provider when its official MCP grows opinionated triage + CI diagnosis.          |
| `polymath-tracker`      | `issue_tracker` — Jira, Linear, GitHub Issues, Azure Boards                             | Triage workflows + provider-agnostic file-bug-from-incident                                              | Demote a provider if its official MCP ships triage automation covering our flow.          |
| `polymath-paging`       | `pager` — PagerDuty, Opsgenie, Splunk On-Call                                          | `page-context` skill discipline; respondToIncident wiring                                                | Demote when an official pager MCP adds a first-class incident-context skill.               |
| `polymath-chat`         | `incident_comms` — Slack, Statuspage (internal team chat + external public status)     | Incident-comms + async-update templates (internal) and severity-mapped public status updates (external)  | Demote when an official MCP ships incident-comms + public-status templates.               |
| `polymath-vuln-scan`    | `vulnerability_scanner` — Snyk, Dependabot, GitHub Advanced Security                    | `triage-vulns` classification (exploitable / reachable / dev-only); Stop hook warns on critical findings | Demote when an official MCP ships classification + open-criticals surfacing.              |

### 3.2 Infra plugins

| Plugin                      | Official surface                                              | Polymath value                                                              | Sunset trigger                                                                |
| --------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `polymath-cloud`      | AWS / GCP / Azure / Terraform official docs and MCP families  | Cross-cloud pattern selection with named cost drivers + flip conditions     | Demote when an official multi-cloud design MCP ships per-provider decision trees. |
| `polymath-kubernetes` | kube docs + several community kube MCPs                       | RBAC grant audit, Pod Security Standards proposals                          | Demote when an official k8s MCP ships an opinionated RBAC + PSS workflow.     |

## 4. Capability mapping

Workflows that need a connector should declare a capability rather
than the concrete plugin (see [`docs/CAPABILITIES.md`](CAPABILITIES.md)).
Projects then map each capability to the configured provider once in
`.polymath/capabilities.yaml`. New providers join the catalog by:

1. Adding the provider token to `registry/schemas/capabilities.json`
   `providers[]` (the recognised vocabulary).
2. Dropping a `bindings/<provider>/binding.json` in the adapter plugin
   (transport + `userConfigKeys` + references).
   `tools/build-capability-index.py` regenerates `providerPlugins.<provider>`
   from that binding — the map is never hand-edited (the `CAPABILITY-INDEX`
   diff-guard and `BINDING-1` enforce this).
3. Updating this audit table with the disclosure fields for the new adapter.

### 4.1 Provider configuration & packaging

A capability plugin may bundle several providers' MCP servers (e.g.
`polymath-observability` ships Datadog + Grafana + Honeycomb + Elastic +
Sentry). Claude Code loads `.mcp.json` statically at session start and cannot
launch only a subset, so:

- **All declared servers register; configure only the provider(s) you use.**
  Every credential env uses a `${VAR:-}` empty default, so an *unconfigured*
  provider can't break MCP config parsing — its server starts idle and fails its
  own auth rather than blocking the whole session.
- **To avoid idle servers, disable the unused ones** via the `/mcp` UI (or
  `disabledMcpjsonServers` in settings).
- **Bindings are the source of truth.** `BINDING-1` checks that every `mcp`
  binding's `server` exists in the plugin's `.mcp.json` and every
  `userConfigKey` exists in `plugin.json` `userConfig`, so the binding model and
  the runtime config cannot drift.

One-plugin-per-provider packaging (so only the installed provider launches) is a
future option the binding model already supports.
Phase 2 (option C). It is intentionally not the default: it would expand the
marketplace and reverse the recent connector consolidation.

### 4.2 MCP package availability

Each connector's `.mcp.json` runs an MCP server via `npx -y <package>`. Some of
those package names are **placeholders**: the vendor's MCP server exists, but it
is distributed as a hosted/remote endpoint, a Go binary, a Python `uvx` package,
or a CLI subcommand — not under that npm name. `npx -y <placeholder>` fails to
download and the server never starts, so the connector is dead-on-install until
the user substitutes the real command.

This is disclosed, not hidden: every affected connector README carries an
`<!-- mcp-package-status -->` callout, and `tools/check-mcp-packages.py`
(`MCP-PKG`, wired into `tools/conformance.sh`) fails the build if a `.mcp.json`
package is neither known-resolving nor disclosed-as-placeholder. The check is
offline (hermetic CI); run it with `--online` to re-verify against npm.

npm resolution status (the `MCP-PKG` gate keeps this table honest;
re-verify any row with `tools/check-mcp-packages.py --online`):

| Package | Connector(s) | npm status |
| --- | --- | --- |
| `@modelcontextprotocol/server-github` | vcs | ✅ resolves |
| `@modelcontextprotocol/server-slack` | chat | ✅ resolves |
| `@sentry/mcp-server` | observability | ✅ resolves |
| `@datadog/mcp-server` | observability | ⚠️ placeholder — does not resolve |
| `@grafana/mcp-server` | observability | ⚠️ placeholder — does not resolve |
| `@honeycomb/mcp-server` | observability | ⚠️ placeholder — does not resolve |
| `@elastic/mcp-server` | observability | ⚠️ placeholder — does not resolve |
| `@pagerduty/mcp-server` | paging | ⚠️ placeholder — does not resolve |
| `@snyk/mcp-server` | vuln-scan | ⚠️ placeholder — does not resolve |
| `@statuspage/mcp-server` | chat | ⚠️ placeholder — does not resolve |
| `@modelcontextprotocol/server-atlassian` | tracker (Jira) | ⚠️ placeholder — does not resolve |
| `@linear/mcp-server` | tracker (Linear) | ⚠️ placeholder — does not resolve |

When a vendor publishes a resolvable npm package (or the connector is repointed
at the real distribution), update the package in `.mcp.json`, move it from
`UNVERIFIED` to `VERIFIED` in `tools/check-mcp-packages.py`, and drop the
README callout. The placeholder connectors stay `experimental` until then.

## 5. Enforcement

`tools/conformance.sh` runs `INTEGRATION-2`: any in-scope plugin whose
`polymath_value` field is empty in this document fails the check.
The audit table above is the source of truth.

Demoting a plugin to `deprecated` is a one-line change to
`.claude-plugin/marketplace.json` plus a `README.md` block naming
the replacement (official MCP, official skill, or another Polymath
plugin).
