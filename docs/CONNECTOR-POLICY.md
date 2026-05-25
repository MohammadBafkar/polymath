# Connector and language plugin policy

This document governs every `polymath-connector-*`, `polymath-lang-*`, and
`polymath-infra-*` plugin. It exists because the most common criticism of
the catalog is that these plugins duplicate official MCPs, official skills,
or official language tooling without adding distinct value.

The policy is simple and load-bearing:

> Official MCPs, official docs, official LSPs, and vendor tools own factual
> and tooling behaviour. Polymath owns workflow shape, critique, safety
> opinions, and artifact discipline. A Polymath connector or language
> plugin is only justified when it adds something the official surface
> does not already give the user.

Every plugin in scope must declare, in its `README.md`, the four fields
below, and the same four fields are mirrored in this document for audit.

## 1. Required disclosure (every connector / lang / infra plugin)

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

If `official_surface.exists == true` and `polymath_value` is empty, the
plugin is in violation of this policy and must be demoted to `deprecated`
in `.claude-plugin/marketplace.json` at the next release.

## 2. Categories

| Category                          | Default tier   | When to promote                                                                            |
| --------------------------------- | -------------- | ------------------------------------------------------------------------------------------ |
| Wraps an official MCP             | `experimental` | Only when a Polymath workflow + golden fixture proves added safety / critique / shape.     |
| No official MCP exists yet        | `beta`         | When Polymath ships at least one workflow that uses the connector + a live golden fixture. |
| Wraps an official skill / LSP     | `experimental` | Same bar as the MCP-wrap case.                                                             |
| Pure workflow / artifact shape    | `beta`         | When at least one external user beyond the maintainer has adopted it.                      |

No plugin in scope promotes to `stable` until the bakeoff (see
`docs/QUALITY-SCORECARD.md`) demonstrates Polymath beats baseline Claude
Code on a case that exercises the plugin.

## 3. Per-plugin audit

The table below records the disclosure for each in-scope plugin. Empty
`polymath_value` columns are flagged for demotion at the next release.

### 3.1 `polymath-connector-*`

| Plugin                                  | Official MCP / source                                                                              | Polymath value                                                          | Sunset trigger                                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `polymath-connector-asana`              | No official MCP yet (Asana REST API)                                                               | Workflow shape for triage; pre-flight permission map                    | Demote when Asana ships an official MCP and our wrapper has no workflow delta.  |
| `polymath-connector-aws`                | Wraps official AWS MCP family                                                                      | Safety opinions (destructive-action confirmation, region pinning)       | Demote when official MCP ships a confirmation mode covering our checklist.      |
| `polymath-connector-azure`              | Wraps official Azure MCP server                                                                    | Same safety-opinion stance as AWS connector                             | Same trigger as AWS connector.                                                  |
| `polymath-connector-cloudflare`         | Wraps official Cloudflare MCP                                                                      | Workflow shape for DNS / Workers safety                                 | Demote when official MCP gates destructive ops by default.                      |
| `polymath-connector-datadog`            | Wraps official Datadog MCP                                                                         | Incident-shaped read-only query patterns; monitor authoring discipline  | Demote when Datadog MCP adds a workflow-quality query language.                 |
| `polymath-connector-elastic`            | Wraps Elastic's MCP                                                                                | Read-only investigative query templates                                 | Same as Datadog.                                                                |
| `polymath-connector-figma`              | Wraps official Figma MCP                                                                           | Critique and code-connect workflow shape (currently thin)               | Demote at next release if no workflow + fixture lands by 2026-08-01.            |
| `polymath-connector-gcp`                | Wraps official GCP MCP                                                                             | Same safety-opinion stance as AWS / Azure                               | Same trigger as AWS connector.                                                  |
| `polymath-connector-github`             | Wraps official GitHub MCP                                                                          | Triage + PR-open workflow shape, owner-aware default                    | Demote when GitHub MCP grows opinionated triage flow.                           |
| `polymath-connector-github-actions`     | Delegates MCP to `polymath-connector-github`                                                       | CI-failure diagnosis workflow                                           | Merge into `polymath-connector-github` if the CI flow stays the only addition.  |
| `polymath-connector-grafana`            | Wraps Grafana MCP                                                                                  | Read-only dashboard query templates                                     | Same as Datadog.                                                                |
| `polymath-connector-honeycomb`          | Wraps Honeycomb MCP                                                                                | Trace-first investigative templates                                     | Same as Datadog.                                                                |
| `polymath-connector-jira`               | Wraps official Jira MCP                                                                            | Triage workflow + file-bug-from-incident shape                          | Demote if Jira MCP ships triage automation that covers our flow.                |
| `polymath-connector-launchdarkly`       | No official MCP yet                                                                                | Pre-registered rollout-plan artifact + experimentToGA integration       | Demote when LD ships an official MCP and our wrapper has no workflow delta.     |
| `polymath-connector-linear`             | Wraps official Linear MCP                                                                          | Same triage workflow shape as Jira connector                            | Same trigger as Jira connector.                                                 |
| `polymath-connector-notion`             | Wraps official Notion MCP                                                                          | None currently — flagged for demotion                                   | Demote at next release if no workflow + fixture lands by 2026-08-01.            |
| `polymath-connector-pagerduty`          | Wraps official PagerDuty MCP                                                                       | `page-context` skill discipline; respondToIncident wiring               | Demote when PagerDuty MCP adds first-class incident-context skill.              |
| `polymath-connector-sentry`             | Wraps official Sentry MCP                                                                          | `triage-error` shape: group context + recent-deploy correlation         | Demote when Sentry MCP ships triage automation covering the four signals.       |
| `polymath-connector-slack`              | Wraps official Slack MCP                                                                           | Incident-comms + async-update templates                                 | Demote when Slack MCP ships incident-comms templates.                           |
| `polymath-connector-snyk`               | Wraps official Snyk MCP                                                                            | `triage-vulns` classification (exploitable / reachable / dev-only)      | Demote when Snyk MCP ships classification beyond raw findings.                  |
| `polymath-connector-statuspage`         | No official MCP yet (Atlassian Statuspage REST API)                                                | Incident-comms drafting tied to severity ladder                         | Demote when Statuspage ships an official MCP and our wrapper has no delta.      |
| `polymath-connector-stripe`             | Wraps official Stripe MCP                                                                          | None currently — flagged for demotion                                   | Demote at next release if no workflow + fixture lands by 2026-08-01.            |
| `polymath-connector-terraform`          | CLI-only (declares `polymath-cli-only` keyword)                                                    | Plan/apply review workflow with safety opinions                         | Demote when an official Terraform MCP covers plan-review.                       |
| `polymath-connector-vercel`             | Wraps official Vercel MCP                                                                          | Deploy-context investigation workflow                                   | Demote when Vercel MCP ships deploy-context automation.                         |

### 3.2 `polymath-lang-*`

| Plugin                          | Official surface                                                       | Polymath value                                              | Sunset trigger                                                              |
| ------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| `polymath-lang-dotnet`          | Official .NET docs + Microsoft Learn skills + Roslyn LSP               | xUnit authoring, nullable adoption, csproj audit workflows  | Merge into `polymath-language-patterns` if it shrinks to ≤ 2 unique skills. |
| `polymath-lang-go`              | Official Go docs + gopls                                               | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-java`            | Official Java docs + Eclipse JDT LS                                    | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-kotlin`          | Official Kotlin docs + kotlin-lsp                                      | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-php`             | Official PHP docs + Intelephense                                       | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-python`          | Official Python docs + Pyright/Pyrefly + ruff/uv                       | ruff workflow, pytest authoring, type-annotation proposal   | Same as `polymath-lang-dotnet`.                                             |
| `polymath-lang-ruby`            | Official Ruby docs + solargraph                                        | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-rust`            | Official Rust docs + rust-analyzer                                     | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-swift`           | Official Swift docs + SourceKit-LSP                                    | None currently — flagged for demotion                       | Demote at next release if no workflow + fixture lands by 2026-08-01.        |
| `polymath-lang-typescript`      | Official TypeScript docs + tsserver + biome                            | Biome workflow, vitest authoring, TS version-migration plan | Same as `polymath-lang-dotnet`.                                             |

### 3.3 `polymath-infra-*`

| Plugin                              | Official surface                                                                          | Polymath value                                                 | Sunset trigger                                                                                                                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `polymath-infra-aws`                | AWS official docs + AWS MCP family                                                        | Cross-account safety opinions, account-pinning checklists      | Merge into `polymath-connector-aws` if the only addition is checklists.                                                                       |
| `polymath-infra-azure`              | Azure official docs + Azure MCP                                                           | Same as AWS infra                                              | Same trigger as `polymath-infra-aws`.                                                                                                         |
| `polymath-infra-docker`             | Docker official docs + `docker` CLI                                                       | Dockerfile audit + multi-stage build patterns                  | Demote when Docker ships an official MCP covering audit.                                                                                      |
| `polymath-infra-gcp`                | GCP official docs + GCP MCP                                                               | Same as AWS infra                                              | Same trigger as `polymath-infra-aws`.                                                                                                         |
| `polymath-infra-kubernetes`         | kube docs + several community kube MCPs                                                   | RBAC grant audit, Pod Security Standards proposals             | Demote when an official k8s MCP ships an opinionated RBAC + PSS workflow.                                                                     |
| `polymath-infra-postgres`           | Postgres official docs + several DB MCPs                                                  | Schema + migration plan workflow shape                         | Demote when an official Postgres MCP ships migration-plan workflow.                                                                           |
| `polymath-infra-redis`              | Redis official docs                                                                       | None currently — flagged for demotion                          | Demote at next release if no workflow + fixture lands by 2026-08-01.                                                                          |
| `polymath-infra-terraform-stack`    | Terraform docs + `terraform` CLI                                                          | Multi-environment stack patterns                               | Demote when an official Terraform MCP covers stack-shape workflows.                                                                           |

## 4. Enforcement

`tools/conformance.sh` includes a new check, `CONNECTOR-2`, that fails when
an in-scope plugin's `polymath_value` field is empty in this document.
The audit table above is the source of truth.

Demoting a plugin to `deprecated` is a one-line change to
`.claude-plugin/marketplace.json` plus a `README.md` block naming the
replacement (official MCP, official skill, or another Polymath plugin).
