---
name: glossary
description: Define shared Polymath vocabulary — artifacts, capabilities/providers/bindings, MCP reuse, routing tiers, workflows — one source of truth when a term needs disambiguating.
---

# glossary

> Single source of truth for Polymath terminology. Reach for this when a term is ambiguous, when two plugins risk using one word for two things, or when onboarding a contributor to the marketplace.

## Lifecycle artifacts

- **PRD** — Product Requirements Document: problem, users, goals, non-goals, requirements, acceptance criteria, metrics. Owner: `polymath-product`.
- **ADR** — Architecture Decision Record (Michael Nygard): context, decision, consequences. Immutable once accepted; superseded, never edited. Owner: `polymath-decisions`.
- **RFC** — Request for Comments: lightweight design document for changes that need group input before commitment. Owner: `polymath-writing`.
- **Acceptance criteria** — Concrete, testable Given/When/Then statements that gate the smallest shippable slice. Owner: `polymath-product`.
- **Postmortem** — Blameless incident retrospective: timeline, impact, contributing causes, action items. Owner: `polymath-incident`.
- **Runbook** — Operator procedure for a known situation: trigger, steps, verification, rollback. Owner: `polymath-writing`.
- **Evidence ledger** — The running log of claims, the evidence behind each, and what would falsify them; the spine of a decision. Owner: `polymath-decisions`.

## Engineering

- **feature-dev** — The TDD loop: write the smallest failing test, make it pass, refactor, repeat. Owner: `polymath-engineering`.
- **code-review** — Correctness + simplification critique of a diff, grounded in the project's review checklist. Owner: `polymath-engineering`.
- **verify-change** — Run repo-appropriate verification (lint, type-check, tests, smoke) and report the evidence. Owner: `polymath-engineering`.
- **read-code** — Orient quickly in an unfamiliar area of a codebase before changing it. Owner: `polymath-engineering`.

## Reasoning primitives

- **thinking primitives** — Small, single-purpose reasoning skills in `polymath-thinking`: `problem-framing`, `brainstorm`, `first-principles`, `5-whys`, `red-team`, `pre-mortem`. `deliberate` composes them and owns only the framing, evaluation, synthesis, and revision around them.

## Workflows

- **Workflow** — A serial, deterministic, paused-and-resumable state machine defined in YAML (`plugins/polymath-flows/workflows/*.yaml`), executed by `bin/polymath-flow`. The user opts in; a workflow is **never auto-started**.
- **flows-lite** — The name of the execution model `bin/polymath-flow` implements: serial (no parallel steps), single-agent (no panels), deterministic, and resumable from persisted state. Contrast with a future parallel/multi-agent runner.
- **Step** — One named action in a workflow with an `invoke` label, a `prompt`, and declared `artifacts`.
- **`invoke:`** — Routing label of the form `<plugin>:<skill>`. It names which skill's procedure to follow; it is not a programmatic call.
- **`requires.capabilities`** — The vendor-neutral dependencies a workflow declares (see *Capabilities* below), resolved against `.polymath/capabilities.yaml` at run time.
- **`mustPass`** — Deterministic post-checks (`fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`) run after the last step; failure pauses the run.
- **`chainsTo`** — A workflow's declaration of the natural next arc on completion. The runner **proposes** it under the same detect → propose → confirm contract; it never auto-runs.
- **Run state** — `${POLYMATH_DATA_DIR:-$HOME/.polymath/data}/polymath-flows/workflows/<id>/state.json`, owned by `bin/polymath-flow`.

## Capabilities & integrations

- **Capability** — A vendor-neutral need (`issue_tracker`, `observability`, `incident_comms`, `pager`, `ci`, `cloud`, `runtime`, `vcs`, `vulnerability_scanner`) declared in [`registry/schemas/capabilities.json`](../../../../registry/schemas/capabilities.json). Workflows target the capability, not a vendor.
- **Provider** — A concrete vendor supplying a capability (e.g. `jira`/`linear` for `issue_tracker`, `datadog`/`honeycomb` for `observability`); listed in that capability's `providers[]`.
- **Binding** — `bindings/<provider>/binding.json` inside a connector plugin: wires one provider to a capability, its transport (`mcp`/`cli`/`skill`), `userConfigKeys`, and provider identity. `providerPlugins{}` is generated from binding paths (`CAPABILITY-INDEX` / `BINDING-1`).
- **Provider identity** — The `mcp` block on a binding (`serverAliases`/`packages`/`remoteUrls`/`envKeys`): the contract used to recognize this provider's MCP server when it is already registered in the host agent. Enforced by `MCP-BINDING`.
- **Integration plugin** — A concept plugin (e.g. `polymath-vcs`, `polymath-observability`) that pairs MCP-dependent skills with the provider's server template (`mcp/servers.json`) that backs them. Detected by `mcp/servers.json` / `bindings/` presence; governed by [`docs/INTEGRATION-POLICY.md`](../../../../docs/INTEGRATION-POLICY.md).
- **MCP-dependent skill** — A skill whose procedure calls an MCP server's tools. The standard split: the **skill is the recipe** (what to do), the **MCP is the tooling** (data/actions). These are the skills `docs/PORTABILITY.md` tags `claude-coupled` — they run fully only where an MCP supplies the tools.
- **MCP reuse (host-only)** — Polymath resolves each provider against MCP servers already registered in the **current** host agent (detected from in-session env markers); a server registered in a different agent is not reusable — its tools are not in this session's tool list. Plugins never auto-register MCP servers; when no host server matches, the provider resolves to `none` and the skill degrades. See [`docs/MCP-REUSE.md`](../../../../docs/MCP-REUSE.md).
- **`mcpResolution`** — The per-provider resolution the SessionStart hook writes into `project-context.json`: `source` (`host`/`none`), the resolved server name, and the host's `toolPrefix`. It is advisory: the scan reads host config files only, so connector skills treat the session's own tool list as authoritative.

## Routing & localization

- **route-signals** — Deterministic, prompt-time routing declarations (a `routing.yaml` sidecar per surface) compiled into `plugins/polymath-core/data/route-signals.json`. Hard signals (`url`/`regex`/`paths`/`diff`) fire a proposal; soft `intents` only rank.
- **Routing tier** — How strongly a surface is signal-backed: `soft` (advisory ranking) or `hard` (a declared deterministic signal that may fire the route hint). Hard-tier surfaces are ratcheted and fixture-backed.
- **`routing.mode`** — The project's routing posture: `hint` (ambient, zero-ceremony), `classify`, or `enforce` (mutating tool calls gated until classified — needs the `polymath-pipeline` plugin).
- **detect → propose → confirm → run** — The contract for workflows and routed surfaces: detect a match, propose it in one line, wait for approval, then run. Never auto-start.
- **Project context** — The resolved `.polymath/project.yaml` snapshot at `${POLYMATH_DATA_DIR}/polymath-core/project-context.json`, consumed by localizing skills. Owner: `polymath-core:project-context`.

## Marketplace

- **Plugin** — Single-responsibility unit of trust, versioning, and distribution (`plugins/polymath-<name>/`).
- **Component** — A skill, command, agent, hook, MCP server, or monitor inside a plugin.
- **Skill vs command** — A skill bundles a procedure with templates/scripts/references; a command is a thin alias (≤ 20 lines) that points at a skill.
- **Always-on listing cost** — Tokens consumed by the `name`+`description` of every skill/command/agent, surfaced to the model every turn.
- **Token budget** — ≤ 400 tokens per plugin always-on; ≤ 1,000 catalog-wide measured. Measured by `tools/token-report.py budget`.
- **Conformance** — The deterministic gates in `tools/conformance.sh` (MANIFEST, SKILL, TEMPLATE, WORKFLOW, SURFACE-INDEX, CAPABILITY-INDEX, BINDING-1, MCP-BINDING, MCP-PKG, INTEGRATION-1/2, DESC-1/2, AGENT-1, FIXTURE-1, DOCS-1/2). `tools/validate-all.sh` runs the authoring subset.
- **Portability** — The agentskills.io export (`tools/export-agents-skills.py`): skills port natively; commands/agents export as converted skills; hooks/workflows/MCP export as support metadata a target host must wire. See [`docs/PORTABILITY.md`](../../../../docs/PORTABILITY.md).

## Quality bar

- Each term has exactly one owner plugin; a term owned by no plugin is a signal the catalog has a gap.
- Definitions match the shipped code/schema, not a previous design (re-check the owning skill or schema when unsure).
- A term that two plugins name differently is a bug to fix, not two glossary entries.

## Output

A definition looked up by term, in the entry shape above — e.g.:

```text
term:        provider
definition:  A concrete vendor supplying a capability (e.g. `datadog` for `observability`).
owner:       the plugin shipping the binding (polymath-observability)
see also:    capability, binding, provider identity
```
