---
artifact: ADR
schemaVersion: 0.1
number: 2
title: Concept/capability-centric plugins (drop vendor-named connectors)
status: accepted
deciders:
  - MohammadBafkar
date: "2026-06-08"
---

# 2. Concept/capability-centric plugins (drop vendor-named connectors)

## Status

accepted

## Context

The discipline plugins (`polymath-engineering`, `polymath-sre`,
`polymath-security`, …) were already role/concept-centric. The integration
plugins were the exception: each was named after a single vendor, even though
`registry/schemas/capabilities.json` already defines each *concept* and maps it
to *multiple* vendors (`vcs` → github / gitlab / azure_devops / bitbucket;
`pager` → pagerduty / opsgenie / splunk_oncall; `incident_comms` → slack /
statuspage; …). The vendor names misrepresented the plugins as single-vendor and
diverged from the capability vocabulary.

## Decision

Make every plugin concept/capability-centric: name integration plugins by the
capability they serve (not by a vendor), with vendors as interchangeable
providers underneath (`bindings/<provider>/binding.json` + per-vendor
`.mcp.json` servers + provider-agnostic skills that resolve the vendor via
`.polymath/capabilities.yaml`). Infra plugins likewise drop their prefix.

The integration / infra plugins and the capability each serves:

| Plugin | Capability / scope |
| --- | --- |
| `polymath-vcs` | `vcs` (+ `ci`) — GitHub, GitLab, Azure DevOps, Bitbucket |
| `polymath-tracker` | `issue_tracker` — Jira, Linear, GitHub Issues, Azure Boards |
| `polymath-observability` | `observability` — design discipline + Datadog / Grafana / Honeycomb / Elastic / Sentry query integration |
| `polymath-paging` | `pager` — PagerDuty, Opsgenie, Splunk On-Call |
| `polymath-chat` | `incident_comms` — Slack (internal) + Statuspage (external) |
| `polymath-vuln-scan` | `vulnerability_scanner` — Snyk, Dependabot, GitHub Advanced Security |
| `polymath-cloud` | cloud-pattern design + Terraform plan-review |
| `polymath-kubernetes` | k8s manifest / RBAC / Pod Security design |

The previous vendor-named integration/infra plugins were renamed or merged into
the above; the old→new mapping lives in git history.

Supporting decisions:

- **Gate detection by artifact, not name.** `INTEGRATION-1`/`INTEGRATION-2`/`MCP-PKG`,
  `sync-integration-policy.py`, and `check-stability-evidence.py` detect
  integration plugins by `.mcp.json` presence and policy-scoped plugins by
  `.mcp.json` **or** `bindings/` (infra plugins carry bindings but no
  `.mcp.json`). The policy-table parser matches any `polymath-*` row. This
  survives the prefix removal and the observability merge.
- **Observability merges discipline + integration.** `polymath-observability`
  now holds both the RED/USE + logging + tracing design skills and the
  Datadog/Grafana/Honeycomb/Elastic/Sentry query skills + bindings (token budget
  366/400). Sentry folded in (it is an observability provider). Statuspage
  folded into `polymath-chat` (internal Slack + external public status, one
  `incident_comms` concept).
- **Real-MCP-only vendor wiring.** Additional vendors (GitLab, Azure DevOps,
  Bitbucket, Teams, Discord, Opsgenie, …) stay listed in the capability vocab as
  the roadmap (the index reports them "aspirational"); a `bindings/<provider>`
  is added when that vendor ships a resolving MCP package, rather than committing
  placeholder servers now.

## Consequences

- **Breaking: published plugin names change.** Anyone who installed the previous
  vendor-named integration or infra plugins must switch to the concept names
  (old→new mapping in git history). No deprecated stubs were kept (hard rename,
  per the maintainer's call).
- Capability resolution is unchanged at runtime — `providerPlugins{}` regenerates
  from the moved bindings' paths.
- The capability vocabulary is now the single source of "which vendors a concept
  supports"; the plugin layer matches it.
- Conformance, `validate-all`, all index `--check` guards, and the catalog build
  pass against the renamed/merged set (36 plugins).
- Supersedes the vendor-per-plugin packaging recorded in
  `docs/INTEGRATION-POLICY.md` §4.1.
