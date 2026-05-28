# Capabilities — provider-agnostic workflows

**Schema:** [`shared/schemas/capabilities.schema.json`](../shared/schemas/capabilities.schema.json) (vocabulary in [`shared/schemas/capabilities.json`](../shared/schemas/capabilities.json)).
**Runtime:** [`plugins/polymath-flows/bin/polymath-flow`](../plugins/polymath-flows/bin/polymath-flow).

## Why this exists

Workflows that talk to external SaaS should describe **what** they need
(an issue tracker, an observability platform, a pager) rather than
**which provider** supplies it. Hard-coding `polymath-connector-pagerduty`
into every incident-response workflow forces every team using opsgenie
to fork. Hard-coding `polymath-connector-jira` into every ticket-filing
step forces every team on Linear to fork. The capability layer
separates the two:

```yaml
# workflow YAML
requires:
  capabilities:
    pager: true
    observability: true
    issue_tracker: true
```

```yaml
# .polymath/capabilities.yaml (in the user's project)
schemaVersion: 1
capabilities:
  pager:         { provider: pagerduty }
  observability: { provider: datadog }
  issue_tracker: { provider: jira }
```

The runner resolves each capability at start time, loads the configured
adapter plugin, and substitutes `${capabilities.<cap>.provider}` /
`${capabilities.<cap>.plugin}` placeholders in step prompts and invoke
labels. Adding a new provider becomes a thin adapter plugin plus one
entry in the vocabulary — never a new top-level catalog plugin.

## Capability vocabulary

Authoritative list in
[`shared/schemas/capabilities.json`](../shared/schemas/capabilities.json).

| Capability              | Providers                                                                 |
| ----------------------- | ------------------------------------------------------------------------- |
| `issue_tracker`         | `jira`, `linear`, `github_issues`, `azure_devops`                         |
| `observability`         | `datadog`, `honeycomb`, `grafana`, `elastic`, `sentry`                    |
| `incident_comms`        | `slack`, `statuspage`                                                     |
| `pager`                 | `pagerduty`, `opsgenie`, `splunk_oncall`                                  |
| `ci`                    | `github_actions`, `azure_devops_pipelines`, `gitlab_ci`, `buildkite`      |
| `cloud`                 | `aws`, `gcp`, `azure`                                                     |
| `runtime`               | `kubernetes`, `ecs`, `cloud_run`, `aci`, `lambda`, `app_service`          |
| `vcs`                   | `github`, `gitlab`, `azure_devops`, `bitbucket`                           |
| `vulnerability_scanner` | `snyk`, `dependabot`, `github_advanced_security`                          |

Capability names are closed; declaring an unknown capability fails
workflow validation. Provider lists are closed per capability;
in-house providers require a PR against `capabilities.json`.

## Project configuration

Create `.polymath/capabilities.yaml` at the root of your repo:

```yaml
schemaVersion: 1
capabilities:
  issue_tracker:
    provider: jira
    # Optional `plugin:` override. Omit to use the catalog default for
    # this provider (looked up from shared/schemas/capabilities.json).
    # plugin: polymath-connector-jira-internal-fork
  observability:
    provider: datadog
  pager:
    provider: pagerduty
  vulnerability_scanner:
    provider: snyk
```

See [`.polymath/capabilities.example.yaml`](../.polymath/capabilities.example.yaml)
for the full annotated template.

Resolution searches in this order, first hit wins:

1. `./.polymath/capabilities.yaml` (project, repo-root)
2. `${CLAUDE_CONFIG_DIR}/polymath/capabilities.yaml` (user / team default)
3. `~/.polymath/capabilities.yaml` (last-resort user default)

There is no merge between layers.

## Workflow authoring

A workflow that uses a capability declares it once in
`requires.capabilities` and references it via placeholders in `invoke`
and `prompt` strings:

```yaml
requires:
  plugins:
    - polymath-core
    - polymath-engineering
  capabilities:
    observability: true     # any configured provider OK
    # observability: { provider: datadog }   # pin to one provider

steps:
  - id: signals
    invoke: ${capabilities.observability.plugin}:query-during-incident
    prompt: |
      Pull ${capabilities.observability.provider} signals for ${inputs.metric}.
      …
```

Placeholders resolved at run time:

- `${capabilities.<cap>.provider}` — provider token (e.g. `datadog`).
- `${capabilities.<cap>.plugin}` — adapter plugin name (e.g.
  `polymath-connector-datadog`).
- `${inputs.<name>}` — workflow input value.
- `${workflow.<slug|id|name>}` — workflow run metadata.

A workflow that pins a provider via `{ provider: datadog }` fails the
run when the project is configured with a different provider for the
same capability. A workflow that says `<cap>: true` accepts whatever
the project picked.

## Runtime resolution

`polymath-flow start` reads `requires.capabilities` and the project
file, then:

1. Validates every declared capability is in the vocabulary.
2. For each capability, looks up the configured provider in the
   project file. Fails if missing.
3. Confirms the configured provider is in the vocabulary's provider
   list for that capability. Fails if not.
4. Resolves the adapter plugin (project override > vocabulary default).
5. Persists the resolved map under `state.json` `capabilities` key and
   the adapter plugins under `effective_plugins`.

Subsequent `polymath-flow next` and `polymath-flow assert` calls expand
`${capabilities.<cap>.<field>}` placeholders from the persisted map, so
mid-run changes to the project file do not affect an in-flight run.

## Workflows that use the capability layer

Four shipped workflows route through capabilities:

| Workflow                  | Capability(ies)                                                |
| ------------------------- | -------------------------------------------------------------- |
| `bumpDependency`          | `vulnerability_scanner`                                        |
| `perfRegression`          | `observability`                                                |
| `incidentRetroToActions`  | `issue_tracker`                                                |
| `respondToIncident`       | `pager` + `observability` + `issue_tracker`                    |

The other workflows declare provider plugins directly via
`requires.plugins`. Both shapes are supported.

## Adding a new provider

1. Add the provider token to the relevant capability's `providers`
   list in [`shared/schemas/capabilities.json`](../shared/schemas/capabilities.json).
2. Add a `providerPlugins.<provider>` entry pointing at the adapter
   plugin name.
3. Ship the adapter plugin (or point at an existing umbrella plugin
   like `polymath-connector-monitoring`).
4. Add a row to [`.polymath/capabilities.example.yaml`](../.polymath/capabilities.example.yaml)
   so users discover the option.

No workflow changes are needed if the new provider exposes the same
skill names as existing providers (e.g. `query-during-incident`,
`file-bug-from-incident`). Skill naming is a convention, not a hard
contract — when an adapter exposes a different skill name, the
workflow must use a concrete `invoke:` rather than the placeholder, or
the adapter must alias the convention name to its own skill.

## Why connector plugins still exist

The capability layer abstracts **what workflows reference**. Adapter
code still lives in concrete plugins because:

- Each provider has provider-specific authentication, idempotency, and
  rate-limit semantics that the adapter encodes.
- MCP server URLs and tool sets vary by provider.
- Skills shipped with each adapter often have provider-specific
  references (e.g. the Datadog skill's monitor IDs vs Grafana's panel
  UIDs).

The layering: **capabilities** (vocabulary) → **adapters** (concrete
plugins) → **workflows** (capability-shaped). Ports-and-adapters at the
catalog level: ports are stable across providers, adapters are not.
