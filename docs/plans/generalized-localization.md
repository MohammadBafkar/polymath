---
artifact: Plan
schemaVersion: 0.1
title: "Generalized project & org localization"
owner: "Mohammad Bafkar"
created: "2026-06-10"
status: accepted
---

# Plan: Generalized project & org localization

## What

Make Polymath localizable to any company or project — as deep and intuitive as a single-company plugin suite — through layered configuration and content packs, while the catalog itself stays 100% vendor-neutral and a repo with no `.polymath/` keeps today's exact behavior.

## Why

Polymath has breadth but localization stops at one flat `project.yaml` (first-hit-wins, no org layer, no machine-local overlay, project workflows invisible to discovery, workflow `extends` documented but unimplemented). A study of an external company-specific pipeline repo showed which mechanisms make deep localization work; this plan imports those mechanisms in generalized form. Constraint that made it necessary: companies must be able to encode their stack, conventions, and hosting reality without forking the catalog.

## Approach

- Layered config: org defaults arrive by pack copy-in at init (no runtime org layer); existing first-hit-wins layers unchanged; gitignored `project.local.yaml` overlay merged above the winning file with a per-key merge policy; one loader, one schema-derived key list.
- Convention packs: a doc taxonomy with templates, `[VERIFY:]` protocol, skills consuming docs by role; a `new-org-pack` scaffolder so any org builds its own pack outside this repo, shipping a `.polymath/` starter plus an `org-defaults` skill that `init-project` detects via the available-skills convention.
- Close verified gaps: workflow `extends` via build-time flattening; project workflow/routing discoverability via tiered, machine-local index fragments; `appStarts`/`connectorAvailable` gates.
- Opt-in pipeline mode (`routing.mode: hint|classify|enforce`) in a new `polymath-pipeline` plugin — never in polymath-core; state under `${CLAUDE_PLUGIN_DATA}`.
- Provenance, feedback, telemetry, and bootstrap scaffolding as fail-open side systems.

## Work breakdown

1. Spike: org-pack config delivery channel. Decision: copy-in — pack ships a `.polymath/` starter + `org-defaults` skill; no runtime org layer. Plugin-dir discovery rejected (undocumented cache/registry internals); data-dir handshake rejected as-specified (`CLAUDE_PLUGIN_DATA` is namespaced per plugin+marketplace, so the handshake dir is unreadable by the loader; hardened sibling-glob variant deferred). — Status: done (2026-06-10)
2. Phase 0 — loader gains only the `project.local.yaml` overlay (existing layers byte-identical), defined merge policy (mappings merge per key, lists/scalars replace), schema keys (`conventions_docs`, `smoke`, `tracker`, `routing`, `attribution`, `artifact_matrix`; opened `prompts`), KNOWN_TOP_KEYS drift-gated against the schema + warn-not-fail unknown keys, delete dead `mcp_servers`, `${project.*:-fallback}` placeholders. — Status: done (2026-06-10)
3. Phase 1 — convention templates in polymath-core `templates/` (zero token cost), `[VERIFY:]` convention doc, 5–8 skills consume by role, `init-project` scaffolds conventions + detects installed org packs (available-skills convention) and proposes their `org-defaults` copy-in, `new-org-pack` scaffolder (conventions/templates/providers + starter `.polymath/`). — Status: done (2026-06-10; 9 consumer skills wired, e2e-tested scaffolder)
4. Phase 2 — `extends` as build-time flattening (provenance hash + drift lint + runner hard-error on runtime `extends`; schema if/then fix), tiered project-workflow index fragment in `${CLAUDE_PLUGIN_DATA}` with trigger-collision drop, project routing overlay (`route-signals.project.json`, SURFACE-2 stays marketplace-internal), `appStarts` (incl. non-blocking `not-applicable`) + `connectorAvailable` across runner/schema/docs. — Status: not started
5. Phase 3 — `polymath-pipeline` plugin: shared root resolver (excluding `$HOME`/config dirs), per-invocation session-namespaced markers, decision log + retention sweep, intake skill (4 confidence dims, plateau stop, never-ask list), classify directive with route-hint precedence, enforce gate (audited kill switch + audited fail-open), generated prose fallback; honor the existing `trust: auto-headless` declaration for read-only surfaces when `routing.mode != hint` (minimum-intervention within the trust contract). — Status: not started
6. Phase 4 — run provenance to `.polymath/runs/` (opt-in, whole-copy, fail-open), feedback loop: capture (conservative, 180d TTL) → evaluate (valid/constructive verdict with evidence, on demand via digest) → apply (auto-draft fixes to project-local localization — conventions docs, skill_overrides, routing signals — for one-confirm apply; catalog-level changes are emitted as proposed patches, never auto-committed), runner telemetry JSONL, 3-layer tracker marking + readback + HITL push. — Status: not started
7. Phase 5 — generic scaffolder in polymath-author (convention-driven, canonical infra bodies, tool-spec handoff), prerequisites-checklist generator; deployer ships as pattern doc only. — Status: not started
8. Phase 6 — plan/spec template upgrades (locked decisions, deferral registry), opt-in visibility markers, summary-first checkpoint in heavyweight doc skills. — Status: not started

## Risks

- Risk: merge semantics silently change existing setups. Mitigation: merge wraps only the two new layers; byte-identical regression fixtures gate Phase 0.
- Risk: version skew — new project.yaml keys hard-fail older loaders. Mitigation: schema/loader widening ships one release before any content uses new keys; unknown reserved keys warn, not exit 2.
- Risk: localization machinery taxes zero-config users. Mitigation: all pipeline hooks live in opt-in `polymath-pipeline`, constant-time early-exit, no new always-on surfaces in polymath-core (61-token headroom).

## Verification

- `tools/conformance.sh --all`, `tools/lint-skills.sh`, `tools/token-budget.sh`, golden suite green at every phase; loader/runner unit tests for merge, flattening, and new gate types; an end-to-end demo org pack (fictional org) localizing a sample repo via two commands.

## Out of scope

- Any vendor-/company-specific content in this catalog — companies localize via their own packs; the studied repo was a pattern source only.
- Runtime org-config layering (hardened data-dir sibling-glob handshake, modeled on the scheduled-queue contract) — revisit if an org reports copy-in defaults drifting stale across repos.
- DAG workflow execution; auto-installation of connectors; autonomous cloud deployer; skill versioning and workflow-schema migration tooling (tracked in LIMITATIONS).

## References

- Comparison + pattern extraction and adversarial critique: session record 2026-06-10 (6 extraction agents, 4-critic panel; ~30 repo claims verified).
