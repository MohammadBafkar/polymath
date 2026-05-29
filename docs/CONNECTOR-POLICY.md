# Connector and infra plugin policy

This document governs every `polymath-connector-*` and
`polymath-infra-*` plugin. It exists because the most common
criticism of any plugin catalog is that connector / infra plugins
duplicate official MCPs, official docs, or vendor tooling without
adding distinct value.

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
[`shared/stability-evidence.json`](../shared/stability-evidence.json)
as `distinct_value_url` and enforced by `tools/check-stability-evidence.py`
(rule `STABILITY-1`). Without it the ledger blocks the promotion.

## 3. Per-plugin audit

The table below records the disclosure for each in-scope plugin.
Empty `polymath_value` columns are flagged for demotion at the next
release.

### 3.1 `polymath-connector-*`

| Plugin                          | Official MCP / source                                                | Polymath value                                                                              | Sunset trigger                                                                            |
| ------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `polymath-connector-datadog`    | Wraps official Datadog MCP                                           | Incident-shaped read-only query patterns; monitor authoring discipline                       | Demote when Datadog MCP adds a workflow-quality query language.                            |
| `polymath-connector-github`     | Wraps official GitHub MCP (incl. GitHub Actions diagnostics)         | Triage + PR-open workflow shape; CI-failure diagnosis on Stop                                | Demote when GitHub MCP grows opinionated triage flow + CI diagnosis.                       |
| `polymath-connector-jira`       | Wraps official Jira MCP                                              | Triage workflow + file-bug-from-incident shape                                               | Demote if Jira MCP ships triage automation covering our flow.                              |
| `polymath-connector-linear`     | Wraps official Linear MCP                                            | Triage workflow shape parallel to Jira                                                       | Same trigger as Jira connector.                                                            |
| `polymath-connector-pagerduty`  | Wraps official PagerDuty MCP                                         | `page-context` skill discipline; respondToIncident wiring                                    | Demote when PagerDuty MCP adds first-class incident-context skill.                         |
| `polymath-connector-sentry`     | Wraps official Sentry MCP                                            | `triage-error` shape: group context + recent-deploy correlation                              | Demote when Sentry MCP ships triage automation covering the four signals.                  |
| `polymath-connector-monitoring` | Wraps Grafana + Honeycomb + Elasticsearch MCPs under one observability capability | Snapshot + trace-walk + bounded-scan disciplines; single capability mapping for all three   | Demote when each upstream MCP ships postmortem-evidence + investigative templates.         |
| `polymath-connector-slack`      | Wraps official Slack MCP                                             | Incident-comms + async-update templates                                                      | Demote when Slack MCP ships incident-comms templates.                                      |
| `polymath-connector-snyk`       | Wraps official Snyk MCP                                              | `triage-vulns` classification (exploitable / reachable / dev-only); Stop hook warns on critical findings | Demote when Snyk MCP ships classification + open-criticals surfacing.                     |
| `polymath-connector-statuspage` | No official MCP yet (Atlassian Statuspage REST API)                  | Incident-comms drafting tied to severity ladder                                              | Demote when Statuspage ships an official MCP and our wrapper has no delta.                 |
| `polymath-connector-terraform`  | CLI-only (declares `polymath-cli-only` keyword)                      | Plan/apply review workflow with safety opinions                                              | Demote when an official Terraform MCP covers plan-review.                                  |

### 3.2 `polymath-infra-*`

| Plugin                      | Official surface                                              | Polymath value                                                              | Sunset trigger                                                                |
| --------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `polymath-infra-cloud`      | AWS / GCP / Azure / Terraform official docs and MCP families  | Cross-cloud pattern selection with named cost drivers + flip conditions     | Demote when an official multi-cloud design MCP ships per-provider decision trees. |
| `polymath-infra-kubernetes` | kube docs + several community kube MCPs                       | RBAC grant audit, Pod Security Standards proposals                          | Demote when an official k8s MCP ships an opinionated RBAC + PSS workflow.     |
| `polymath-infra-postgres`   | Postgres official docs + several DB MCPs                      | Schema + migration plan workflow shape                                      | Demote when an official Postgres MCP ships migration-plan workflow.           |

## 4. Capability mapping

Workflows that need a connector should declare a capability rather
than the concrete plugin (see [`docs/CAPABILITIES.md`](CAPABILITIES.md)).
Projects then map each capability to the configured provider once in
`.polymath/capabilities.yaml`. New providers join the catalog by:

1. Adding the provider token to `shared/schemas/capabilities.json`.
2. Pointing `providerPlugins.<provider>` at the adapter plugin name.
3. Updating this audit table with the disclosure fields for the new
   adapter.

## 5. Enforcement

`tools/conformance.sh` runs `CONNECTOR-2`: any in-scope plugin whose
`polymath_value` field is empty in this document fails the check.
The audit table above is the source of truth.

Demoting a plugin to `deprecated` is a one-line change to
`.claude-plugin/marketplace.json` plus a `README.md` block naming
the replacement (official MCP, official skill, or another Polymath
plugin).
