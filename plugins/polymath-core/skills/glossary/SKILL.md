---
name: glossary
description: Shared vocabulary for Polymath plugins (PRD, ADR, RFC, mustPass, flows-lite, …). Use when terms need disambiguating.
---

# glossary

> Single source of truth for Polymath terminology. Reach for this when a term is ambiguous or when onboarding a new contributor.

## Lifecycle artifacts

- **PRD** — Product Requirements Document. Problem, users, goals, non-goals, requirements, acceptance criteria, metrics. Owner: `polymath-product`.
- **ADR** — Architecture Decision Record (Michael Nygard). Context, decision, consequences. Owner: `polymath-decisions` (future tier).
- **RFC** — Request for Comments. Lightweight design document for changes that need group input. Owner: `polymath-writing` (future tier).
- **Acceptance criteria** — Concrete, testable Given/When/Then statements that gate the smallest shippable slice. Owner: `polymath-product`.
- **Postmortem** — Blameless incident retrospective: timeline, impact, 5-whys, action items. Owner: `polymath-incident` (future tier).

## Engineering

- **Feature-dev (TDD loop)** — Write the smallest failing test, make it pass, refactor, repeat. Owner: `polymath-engineering`.
- **Code review** — Correctness + simplification critique. Owner: `polymath-engineering`.
- **Verify-change** — Run repo-appropriate verification (lint, type-check, tests, smoke). Owner: `polymath-engineering`.
- **Read-code** — Orient quickly in an unfamiliar area of a codebase. Owner: `polymath-engineering`.

## Release

- **Conventional Commits** — `type(scope): summary` commit format.
- **CHANGELOG** — User-facing record of changes, grouped by `[Unreleased]` + release tags.
- **Release notes** — Customer-facing announcement; broader audience than CHANGELOG.

## Workflows (flows-lite)

- **flows-lite** — Polymath's v0.1 workflow runner: serial, deterministic, paused-and-resumable.
- **Step** — One named action in a workflow with an `invoke` capability label.
- **`invoke:`** — Routing label of the form `<plugin>:<capability>`. v0.1 is a label, not a programmatic slash-command call.
- **Guard** — Precondition (e.g., `git status` clean) checked before the first step.
- **`mustPass:`** — Deterministic checks (`fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`) run after the last step. Failure pauses the workflow.
- **Workflow state** — `${CLAUDE_PLUGIN_DATA}/workflows/<id>/state.json`. Owned by `bin/polymath-flow`.

## Marketplace

- **Plugin** — Single-responsibility unit of trust, versioning, and distribution.
- **Component** — A skill, command, agent, hook, MCP, or monitor inside a plugin.
- **Always-on listing cost** — Tokens consumed by component descriptions surfaced to the model every turn.
- **Token budget** — ≤ 400 per plugin; ≤ 1,500 MVP total. Measured by `tools/token-budget.sh`.

## Capabilities & integrations

- **Capability** — A vendor-neutral need (`issue_tracker`, `vcs`, `observability`, `pager`, …) declared in `registry/schemas/capabilities.json`. Workflows target the capability, not a vendor.
- **Provider** — A concrete vendor that supplies a capability (e.g. Jira / Linear for `issue_tracker`); listed in the capability's `providers[]`.
- **Binding** — `bindings/<provider>/binding.json` inside a plugin: wires one provider to a capability plus its MCP server + `userConfig` keys. `providerPlugins{}` is generated from binding paths (`CAPABILITY-INDEX` / `BINDING-1`).
- **Integration plugin** — A concept plugin (e.g. `polymath-vcs`, `polymath-chat`) that pairs MCP-dependent skills with the `.mcp.json` server(s) that back them. Detected by `.mcp.json` / `bindings/` presence; governed by [`docs/CONNECTOR-POLICY.md`](../../../../docs/CONNECTOR-POLICY.md).
- **MCP-dependent skill** (informally "MCP-based skill") — A skill whose procedure calls an MCP server's tools. Note the standard Skills↔MCP distinction: the **skill is the recipe** (what to do), the **MCP is the tooling** (data/actions) — complementary, not the same thing. These are the skills `docs/PORTABILITY.md` tags `claude-coupled`: they run fully only where the MCP is configured, unlike a portable, pure-procedure skill.
