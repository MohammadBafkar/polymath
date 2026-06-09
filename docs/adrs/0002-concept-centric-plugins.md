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
plugins were the exception: they were named after a single vendor
(`polymath-connector-github`, `-pagerduty`, `-slack`, `-snyk`, …) even though
`registry/schemas/capabilities.json` already defines each *concept* and maps it
to *multiple* vendors (`vcs` → github/gitlab/azure_devops/bitbucket; `pager` →
pagerduty/opsgenie/splunk_oncall; `incident_comms` → slack/statuspage; …). Two
connectors (`tracker`, `observability`) had already been consolidated to the
concept shape. The vendor names misrepresented the plugins as single-vendor and
diverged from the capability vocabulary.

## Decision

Make every plugin concept/capability-centric. Drop the `connector-`/`infra-`
prefixes; name integration plugins by the capability they serve, with vendors as
interchangeable providers underneath (`bindings/<provider>/binding.json` +
per-vendor `.mcp.json` servers + provider-agnostic skills that resolve the
vendor via `.polymath/capabilities.yaml`).

Renames / merges:

| From | To |
| --- | --- |
| `polymath-connector-github` | `polymath-vcs` |
| `polymath-connector-tracker` | `polymath-tracker` |
| `polymath-connector-pagerduty` | `polymath-paging` |
| `polymath-connector-slack` (+ `-statuspage`) | `polymath-chat` |
| `polymath-connector-snyk` | `polymath-vuln-scan` |
| `polymath-connector-observability` (+ `-sentry`) | merged into `polymath-observability` |
| `polymath-infra-cloud` | `polymath-cloud` |
| `polymath-infra-kubernetes` | `polymath-kubernetes` |

Supporting decisions:

- **Gate detection by artifact, not name.** `INTEGRATION-1`/`INTEGRATION-2`/`MCP-PKG`
  and `sync-integration-policy.py` now detect integration plugins by `.mcp.json`
  presence and policy-scoped plugins by `.mcp.json` **or** `bindings/` (infra
  plugins have bindings but no `.mcp.json`). The policy-table parser matches any
  `polymath-*` row. This survives the prefix removal and the observability merge.
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

- **Breaking: published plugin names change.** Anyone who installed
  `polymath-connector-*` / `polymath-infra-*` must switch to the concept names.
  No deprecated stubs were kept (hard rename, per the maintainer's call).
- Capability resolution is unchanged at runtime — `providerPlugins{}` regenerates
  from the moved bindings' paths (observability providers → `polymath-observability`,
  statuspage → `polymath-chat`, etc.).
- The capability vocabulary is now the single source of "which vendors a concept
  supports"; the plugin layer matches it.
- Conformance, `validate-all`, all index `--check` guards, and the catalog build
  pass against the renamed/merged set (36 plugins).
- Supersedes the vendor-per-plugin packaging recorded in
  `docs/INTEGRATION-POLICY.md` §4.1; that section's "kept separate" note for
  slack/pagerduty/statuspage is now obsolete (they are concept plugins).
