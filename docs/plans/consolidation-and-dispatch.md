---
artifact: Plan
schemaVersion: 0.1
title: "Consolidation & Dispatch: one surface registry, one binding model"
owner: "Mohammad Bafkar"
created: "2026-06-07"
status: done
review_date: "2026-09-07"
---

# Plan: Consolidation & Dispatch — one surface registry, one binding model

> Canonical home of the dispatch-layer model that `route-hint.py` and
> `polymath-profiles.json` already cite. This doc defines Layers 1–4 and the
> consolidation that unifies routing, triggering, resumption, and connectors.
>
> **This is now a RECORD, not a forward plan.** It began as a plan; all five
> phases shipped 2026-06-07. The **Approach / Risks / Verification** sections
> below preserve what was *targeted* — several targets were missed, falsified, or
> shipped as declared-but-inert metadata. Read **[Outcome (measured)](#outcome-measured)**
> for the honest scorecard: it supersedes the forward-looking claims wherever they
> disagree, with held-out measurements and the one premise still unmeasured.

## What

Collapse the marketplace's three parallel detection mechanisms and its
per-service connector model into **one compiled surface registry** (skills,
workflows, and tools each declare their own routing + capability needs in
frontmatter) plus **one capability → provider → binding registry** (providers
are drop-in folders, not plugin forks). One dispatcher hook and one resumer
consume both. This makes every surface discoverable the way workflows already
are, makes connectors genuinely tech-agnostic, lets *tools* be added like
skills, and turns "automatic resume" and "graduated autonomy" into one shared
`trust` axis — without weakening the propose-before-run default for interactive
sessions.

## Why

Four asks — plugin dispatch/discoverability, automatic workflow resumption,
easier/automatic triggering, and tech-agnostic connectors — are four symptoms
of one root cause: **routing knowledge and provider knowledge are scattered and
hand-synced instead of declared once and compiled.** Evidence:

- **Drift by design.** `plugins/polymath-core/data/route-signals.json` (15
  rules) carries a `_note` that its workflow rows "mirror
  `polymath-flows/data/workflow-detect.json` (27 rows); keep them loosely in
  sync." Two hand-maintained copies of the same facts.
- **The 1-of-N problem is solved only for workflows.** `route-hint.py` exists
  because "the model is reliable at 1-of-3 and unreliable at 1-of-131"
  (`route-hint.py` lines 22-23) — yet of **149 skills, exactly 4** get
  deterministic dispatch. The other 145 rely on the model reading ≤200-char
  descriptions: precisely the 1-of-N case the hook was built to defeat. There is
  no `build-skill-index` analogue to `build-workflow-index.py`.
- **A third, redundant detection layer.** Six connectors ship **8 bespoke bash
  detectors** that each re-parse the prompt and `echo` a "fetch via the MCP"
  hint (e.g. `detect-ticket-key.sh`). On one prompt with the SRE profile
  installed, ~4 connector detectors + core route-hint each spawn `python3` on
  the identical payload; nobody owns the union or dedupes overlaps.
- **"Provider-agnostic" connectors are nominal.** `connector-observability`'s
  `.mcp.json` **hardcodes 4 MCP servers** (datadog/grafana/honeycomb/elastic);
  `tracker` hardcodes 2. Installing observability launches four `npx` servers;
  you configure one, three idle or fail. Adding a provider (GitLab, New Relic,
  Opsgenie, Azure DevOps) requires forking the connector — yet
  `shared/schemas/capabilities.json` already *lists* those providers, so the
  vocabulary advertises integrations that do not exist (`providers[]` ~30,
  `providerPlugins{}` ~10).
- **No unit of integration smaller than a plugin.** `CONNECTOR-1` *requires*
  `.mcp.json` + per-key `userConfig` on each connector — the schema assumes
  connector == one MCP-wrapper-plugin, which structurally fights "tools added
  like skills."
- **Resume is durable but never automatic.** State persists and paused runs are
  surfaced at SessionStart, but a run only becomes `paused` on explicit `fail`
  (`polymath-flow` line 935); an abandoned run stays `active` and SessionStart
  only surfaces `paused` (`session-start.sh` line 77) — the most common
  interruption (context death, `/clear`) produces the one invisible state.
- **Provenance is broken.** `route-hint.py` and `profiles.json` cite this exact
  file by "Dispatch Layer 1 / Layer 3" — and it did not exist until now.

See `LIMITATIONS.md` (§4 known gaps, §2 connector philosophy) and `AGENTS.md`
(conformance table) for the constraints this plan must respect.

## Background — what exists today

| Concern | Mechanism | Coverage | Sync |
| --- | --- | --- | --- |
| Install discovery | `polymath-profiles.json` (7 spines) | 40 plugins → 7 choices | manual |
| Prompt routing | `route-hint.py` + `route-signals.json` | 15 (11 wf + 4 skill) | manual |
| Workflow visibility | `workflow-index.min.json` (SessionStart) | 27 workflows | built |
| Connector hints | 8 bash detectors | ~6 services | per-script |
| Skill discovery | always-on descriptions | 149 skills | n/a |
| Resume | `polymath-flow` state machine + SessionStart | paused runs only | n/a |
| Provider binding | per-connector `.mcp.json` | ~10 wired | manual |

## Dispatch layers (canonical model)

The model the codebase references. This plan keeps the numbers stable so
existing citations resolve.

- **Layer 1 — Install-time.** `polymath-profiles.json` role spines: pick one
  profile, not 1-of-40. *(cited by `profiles.json`)*
- **Layer 2 — Session-time.** SessionStart injects the compiled, always-on
  index of runnable surfaces (today: workflows; after Phase 1: all surfaces)
  with a propose-before-run instruction.
- **Layer 3 — Prompt-time.** `route-hint.py` deterministic hard-signal
  dispatch on `UserPromptSubmit`; narrows to a 1-of-3 proposal, never auto-runs.
  *(cited by `route-hint.py`)*
- **Layer 4 — Event-time *(new)*.** `PostToolUse` / `Stop` triggers propose the
  matching surface from what just happened (a failing test → `bugTriage`; a
  dependency-adding diff → `bumpDependency`), through the same registry.

Layers 2–3 read **one** compiled registry (`build-surface-index.py` output) and
hand-maintain nothing. Layer 4's event rules are the exception: they live in a
separate hard-coded table in `event-trigger.py` (one rule today), not the
compiled registry — see [Outcome](#outcome-measured). The "all four" unification
is aspirational, not shipped.

## Approach

Five phases, each independently shippable and reversible behind a flag. Phase 1
is the keystone; 2–3 generalize connectors; 4–5 add autonomy and resilience.

1. **Surface registry (keystone).** Generalize `build-workflow-index.py` →
   `build-surface-index.py`; every skill/workflow/tool declares `triggers:` +
   `capabilities:` in frontmatter; one builder compiles `surface-index.json` +
   `route-signals.json` (now a build *output*) + the SessionStart index. Delete
   the 8 connector bash detectors and the route-signals↔workflow-detect
   hand-sync.
2. **Provider bindings.** Connectors become capability plugins; each provider is
   a drop-in `bindings/<provider>/` (transport spec + config keys + tool
   reference). The active provider's `.mcp.json` is *generated* from
   `.polymath/capabilities.yaml`; only the configured server launches.
   *(Planned — the Phase-2 spike falsified this; Option A shipped instead and all
   bundled servers still launch. See [Outcome](#outcome-measured).)*
   `capabilities.json` `providerPlugins{}` becomes derived, not aspirational.
3. **Tools as surfaces.** Define a `tools/<name>/` sub-plugin unit (a small
   manifest: how to invoke — MCP/CLI/HTTP — + reference + config keys) that
   declares `triggers:`/`capabilities:` and is discoverable + dispatchable
   through the Phase-1 registry. This is "tools added like skills."
4. **Trust axis + event triggering.** Add `trust: propose|auto-headless|auto`
   to every surface; add a generic `PostToolUse`/`Stop` trigger hook and arc
   `chainsTo:` hand-offs. Interactive default stays `propose`.
5. **Resumability hardening.** `PreCompact`/`Stop` checkpoint of the in-flight
   step; surface stale-`active` runs; resume by `run_id` with name→id
   disambiguation; TTL/GC of run dirs; enforce-or-delete the `budget.json` stub;
   auto-resume gated by the Phase-4 `trust` axis.

## Work breakdown

Each step is independently completable and produces an observable result.

1. Write the surface-frontmatter schema (`triggers`, `capabilities`, `trust`,
   `chainsTo`) and add it to `shared/schemas/`. *(schema file exists + validates)*
2. Build `tools/build-surface-index.py` that compiles all SKILL.md + workflow
   YAML into `surface-index.json`, emits `route-signals.json` and the
   SessionStart index as outputs. *(`--check` is green on a fresh build)*
3. Backfill `triggers:` onto the 15 surfaces already in `route-signals.json`;
   prove byte-identical output to the current hand-written table. *(diff empty)*
4. Roll `triggers:` to all remaining skills in waves; builder enforces global
   trigger uniqueness. *(coverage report: N/149 skills dispatchable)*
5. ~~Replace the 8 connector bash detectors with `triggers:` on their skills.~~
   **Reassigned 2026-06-07:** implementation showed these are two mechanisms — 5
   `UserPromptSubmit` prompt-detectors (tool-pull hints) move to **Phase 3**
   (tools-as-surfaces); 3 `Stop` end-of-turn nudges move to **Phase 4** (event-time
   triggering, the pattern Gap 3 generalizes). See Verification updates.
6. Define `bindings/<provider>/binding.json` schema (transport: server|cli|http,
   env/config keys, references). *(schema + one example binding)*
7. Convert `connector-observability` to bindings; generate `.mcp.json` from the
   active provider. *(installing it launches exactly 1 server)*
8. Add a reference *new* provider (e.g. GitLab `vcs`/`ci` or New Relic
   `observability`) as a binding only — no edits to existing files. *(provider
   works; `providerPlugins{}` regenerates to include it)*
9. Convert the remaining 8 connectors to bindings; collapse provider-named
   skills (`jira-triage`/`linear-triage`) into one capability-resolved skill.
10. Define the `tools/<name>/` manifest + `TOOL-1` schema; expose binding tool
    docs as tool surfaces in the Phase-1 index. *(a tool appears in dispatch)*
11. Add `trust:` handling to `route-hint` + run-workflow contract; `auto-headless`
    runs without asking when non-interactive. *(Shipped as DECLARED metadata only —
    no executor honors it, 0 surfaces flipped; the "fixture auto-runs" criterion was
    NOT met. See [Outcome](#outcome-measured).)*
12. Add the generic `PostToolUse`/`Stop` trigger hook + `chainsTo` arc hand-off.
    *(failing-test fixture proposes `bugTriage`; `respondToIncident` proposes
    `incidentRetroToActions`)*
13. Add `PreCompact`/`Stop` checkpoint to `polymath-flow`; persist in-flight step
    summary. *(killed mid-step run resumes to the correct step)*
14. Surface stale-`active` runs at SessionStart; resume by `run_id`; add TTL/GC;
    enforce or remove `budget.json`. *(stale run appears; old runs GC'd)*

## Conformance changes (CI)

The repo is conformance-driven; this plan adds/changes gates rather than
documentation alone.

- **SURFACE-INDEX *(new)*** — `surface-index.json` + emitted `route-signals.json`
  match a fresh `build-surface-index.py` build (diff-guard + injected-index
  token ceiling). Supersedes `WORKFLOW-INDEX` (which becomes a subset).
- **ROUTE-TRIGGER *(extended)*** — `route-triggering.py`, `workflow-triggering`, and
  `skill-triggering` fold into one harness over the union of surfaces.
- **WORKFLOW-2 → SURFACE-2 *(extended)*** — trigger-phrase global uniqueness
  enforced across **all** surfaces (skills + workflows + tools), not just
  workflows. Reuses the `DESC-1` disambiguation floor.
- **CONNECTOR-1 *(reframed)*** — "must declare ≥1 provider *binding*" replaces
  "must ship `.mcp.json`"; `.mcp.json` may be a generated artifact.
- **BINDING-1 *(new)*** — each binding's `provider` must appear in
  `capabilities.json` `providers[]`; `providerPlugins{}` is *derived* from
  bindings (no provider advertised without a binding).
- **TOOL-1 *(new)*** — tool manifests validate against the tool schema.
- **TRUST-1 *(new)*** — `trust` defaults to `propose`; lint forbids `auto` for
  any surface that writes outside `docs/`.

## Risks

- Risk: per-surface `triggers:` bloats frontmatter and re-introduces routing
  collisions. Mitigation: builder enforces global uniqueness at compile time
  (extends `DESC-1`/`SURFACE-2`); CI fails on collision — drift cannot ship.
- Risk: `auto` trust is a footgun (an auto-run `securityFinding` that
  force-pushes). Mitigation: opt-in per project, never default; `TRUST-1` lint
  forbids `auto` for write-outside-`docs/` surfaces; `auto-headless` is the safe
  middle tier.
- Risk: Claude Code may load a plugin's `.mcp.json` statically and not run a
  generator. Mitigation: **validate this assumption first** — fall back to a
  `polymath-core` SessionStart step that writes the resolved `.mcp.json` into
  plugin data, or commit per-provider files toggled by config. Phase 2 is gated
  on this spike.
- Risk: current `.mcp.json` package names (`@datadog/mcp-server`,
  `@honeycomb/mcp-server`, `@linear/mcp-server`, …) may be placeholders that do
  not resolve on npm. Mitigation: bindings make each provider's transport
  explicit and individually testable; audit resolution per binding during
  conversion.
- Risk: extending deterministic dispatch to 149 skills makes the hint hook
  noisy. Mitigation: keep the hard-signal floor + `MIN_SCORE` + 1-of-3 cap
  (`route-hint.py` lines 33-36); ship a hit-rate measurement before widening.
- Risk: 40 plugins touched; coordination + breakage. Mitigation: every phase is
  flag-gated, independently shippable, and reversible; `route-signals.json`
  keeps its current path as a generated artifact so `route-hint.py` is unchanged.
- Risk: binding indirection is pure overhead for single-provider shops.
  Mitigation: indirection is author-time only; the generated `.mcp.json` makes
  runtime identical to today.
- Risk: **every dispatch layer is coupled to Claude Code-specific host
  semantics** — `UserPromptSubmit`, `PostToolUse`, `Stop`, `SessionStart`,
  `PreCompact` hooks and `.mcp.json` static load. None of it ports to Cursor /
  Codex / Goose, and the Phase-2 spike already hit one such limit (`.mcp.json` is
  read statically, *before* SessionStart). `PORTABILITY.md` covers the SKILL.md
  format, **not** this dispatch layer. Mitigation: the surfaces stay portable
  (routing / trust / bindings are plain declarations consumable by any host); only
  the *hooks* that consume them are Claude-Code-bound. A host hook-contract change
  is a first-class breakage risk, not a footnote.

## Verification

- `build-surface-index.py --check` is green; `route-signals.json` and
  `workflow-detect.json` are build outputs (grep shows no hand-sync `_note`).
- Deterministic-dispatch coverage reaches **20/149 skills** (≈13%) — *not* the
  "measured majority" this bullet originally claimed; thinking skills with no hard
  signal intentionally stay description-matched. Hit-rate is now **measured**
  held-out (`tools/route-eval.py`): precision 9/9, false-positives 0/7,
  naturalistic reach 1/16. See [Outcome](#outcome-measured).
- ❌ **Not delivered as written.** The Phase-2 spike falsified "exactly one MCP
  server" (Claude Code loads `.mcp.json` statically). Shipped **Option A**: all
  bundled servers launch, hardened with `${VAR:-}`. What *did* hold: adding a
  provider binding needs **zero** edits to existing files, and `providerPlugins{}`
  is generated to match. "Exactly one server" needs Option C (deferred). See
  [Outcome](#outcome-measured).
- A run killed between `next` and `complete` is surfaced at the next SessionStart
  (stale-`active`) and resumes to the correct step; `budget.json` is enforced or
  gone; run dirs GC by TTL.
- ⚠️ **Declared, not enforced.** `trust: auto-headless` compiles into
  route-signals and `route-hint` annotates it descriptively, but **no executor
  consumes it and 0 surfaces are flipped** — every surface still proposes-first,
  interactive and headless alike. Autonomy is forward-looking metadata pending an
  enforcing consumer. See [Outcome](#outcome-measured).
- All existing gates plus the new ones (`SURFACE-INDEX`, `BINDING-1`, `TOOL-1`,
  `TRUST-1`) pass; bakeoff + triggering fixtures stay green.
- This file exists; `route-hint.py` and `profiles.json` "Layer" citations
  resolve to the layer model above.

## Out of scope

- Building a scheduler. `queue.json` stays externally-fed (cron / GitHub Action
  / Anthropic Routine), per the existing design in `session-start.sh`.
- Changing the agentskills.io v1.0 SKILL.md format or the cross-harness
  portability contract.
- Net-new provider integrations beyond 1–2 reference bindings that *prove* the
  model.
- Parallel/fanout workflow execution (`topology=fanout` stays serial; separate
  concern).
- Any maturity promotion; the `stability-evidence.json` / bakeoff gates are
  unchanged.
- Re-enabling live-model CI fixtures (tracked separately in `LIMITATIONS.md` §4).

## Implementation status

Plan-only; nothing built yet. Update the Status column as phases land, and
append dated notes under Verification updates (per repo plan-progress
convention).

| Phase | Scope | Gaps closed | Status |
| --- | --- | --- | --- |
| 1 | Surface registry (keystone) | dispatch/discovery (1), part of triggering (3) | **Done (2026-06-07)** — route-signals.json now generated; **20/149 skills** + 11/27 workflows routable (breadth wave landed); SURFACE-INDEX gate green |
| 2 | Provider bindings | connectors (4) | **Done (2026-06-07)** — data-model (20 bindings → generated `providerPlugins{}`) + **Option A** packaging (env-default hardening + binding↔config consistency gate + /mcp-disable docs); C-capable for later |
| 3 | Tools as surfaces | connectors (4), feeds (1)/(3) | **Done (2026-06-07)** — `tools/<name>/` unit (tool.json + routing.yaml); jira/linear/sentry tool surfaces replace 5 bash detectors (PR/incident subsumed by reviewPR/respondToIncident); TOOL-1 via SURFACE-INDEX |
| 4 | Trust axis + event triggering | triggering (3) | **Done (2026-06-07)** — trust axis (route-hint surfacing + TRUST-1); `chainsTo` arc hand-offs (engine surfaces on completion + dangling guard); PostToolUse event-trigger (failed tests → bugTriage) |
| 5 | Resumability hardening | resume (2) | **Done (2026-06-07)** — SessionStart surfaces active/stale/mid-step runs; `last_active` + `gc` + in-flight `checkpoint`; `budget.json` stub removed; +5 unit tests |

### Verification updates

- **2026-06-07 — Phase 1 landed.** `tools/build-surface-index.py` is now the single
  producer of `plugins/polymath-core/data/route-signals.json` (formerly hand-maintained,
  carrying a "keep loosely in sync" note) plus a new `surface-index.json` catalog. Each
  surface declares routing in a sidecar validated by
  `shared/schemas/surface-routing.schema.json` — skills in `skills/<s>/routing.yaml`,
  workflows in `plugins/polymath-flows/routing/<name>.yaml` (outside the `workflows/*.yaml`
  glob, so the flows validator never sees them). The 15 pre-existing rules were migrated
  with **behaviour proven unchanged**: all 7 original ROUTE-TRIGGER fixtures still pass.
  Widening proof: `polymath-writing:rfc` + `polymath-devops:dockerize` became
  deterministically routable with *nothing but a sidecar* (+2 new fixtures) — coverage
  4→6 skills, 9/9 fixtures green. New `SURFACE-INDEX` gate wired into `conformance.sh`
  (`--check` drift-guard + `--strict` SURFACE-2 global signal uniqueness). Full battery
  green: `conformance: OK`, validate-all / lint-skills / token-budget (6898 ≤ 10000) OK.
- **Plan refinement (step 5 reassigned).** The 8 connector bash detectors are two
  mechanisms, not one: 5 `UserPromptSubmit` prompt-detectors (ticket-key / incident-URL /
  Sentry-issue → "pull via MCP") are tool-pull hints best modelled as routable connector
  *tools* (Phase 3); 3 `Stop` end-of-turn nudges (github suggest-pr / check-recent-ci,
  snyk check-criticals) are event-time triggers (Phase 4 — the pattern Gap 3 *generalizes*,
  not deletes). Folding them into Phase 1 would have forced a propose-a-skill semantic onto
  a context hint, so they stay in place until their natural phase.
- **2026-06-07 — Phase 5 landed (resumability, Gap 2).** The biggest hole was that the
  SessionStart hook surfaced only `paused` runs, so a run interrupted mid-flight (context
  death / `/clear`) stayed `active` and went *invisible*. Fixed: `polymath-flow` now stamps
  `last_active` on `start`/`next`/`complete`/`resume`; the `polymath-core` SessionStart hook
  surfaces **in-progress (active) runs too**, flagging any with `last_active` ≥ 2 days old as
  stale, with `run_id`-keyed resume hints. Added a `gc` subcommand (prunes terminal runs older
  than `--days`, default 30; never touches active/paused unless named) and **removed the
  `budget.json` stub** (written on every start, read by nothing, advertising ceilings never
  enforced — honest per LIMITATIONS.md §4 "no cost telemetry"). `resume-workflow` SKILL updated
  to list both buckets. +4 unit tests (43 pass); WORKFLOW-1 green on all 27 workflows.
  **Deferred:** the `PreCompact`/`Stop` in-flight checkpoint (work-breakdown #13) — re-evaluated
  as low value, because `next` is idempotent (it re-issues the current step from
  `current_step_index`, which only advances on `complete`), so an interrupted step is correctly
  re-offered; only un-reconcilable partial side-effects remain, which need agent cooperation.
- **2026-06-07 — Phase 2 spike resolved: premise FALSIFIED.** The plan assumed Phase 2 could
  "generate `.mcp.json` from the active provider" so only the configured server launches. A
  Claude Code capabilities spike found: (a) `.mcp.json` is read **statically at session start**
  from the plugin root; (b) an unset `${VAR}` makes Claude Code **fail to parse the whole
  config** (so today's bundle-all-providers connectors are themselves fragile); (c) **no
  supported conditional/dynamic server selection** exists — SessionStart hooks fire *after* MCP
  config load, and generated `.mcp.json` is undocumented/unsupported. Net: "only the configured
  provider launches from one multi-provider plugin" is **not achievable at runtime today.**
  Three viable designs, each a real trade-off — option C reverses the recent 51→40
  consolidation, so this is a **maintainer decision, not a default to pick**:
  - **A — Lean bundle + docs.** One capability plugin, all servers, `${VAR:-}` defaults so unset
    providers don't crash config parse; document `/mcp` disable. *Pro:* fewest plugins. *Con:*
    idle servers + startup cost.
  - **B — Inline `plugin.json` `mcpServers` + user shadow.** As A but inline; users add a
    local-scope override to pick one. *Pro:* clean ship. *Con:* users must understand scopes.
  - **C — Generated single-provider plugins.** A `bindings/<provider>/binding.json` is the
    authoring unit; a builder emits one thin single-provider connector plugin per binding.
    *Pro:* only the installed provider launches (the goal); "add a provider = drop a folder +
    rebuild"; `providerPlugins{}` becomes generated/honest. *Con:* more marketplace entries —
    reverses 51→40. Best paired with install **profiles** so users pick a role, not N plugins.
  The binding *data model* (bindings as authoring unit + generated `providerPlugins{}`) is worth
  doing under any option; only the runtime packaging differs.
- **2026-06-07 — Phase 2 data-model landed** (maintainer chose "binding model, defer packaging").
  Added [`shared/schemas/binding.schema.json`](../../shared/schemas/binding.schema.json) +
  `tools/build-capability-index.py`, the single producer of `capabilities.json`
  `providerPlugins{}`. Bootstrapped **20** `bindings/<provider>/binding.json` across the connector
  and infra plugins from the existing wiring; the generator reproduces `providerPlugins{}`
  **byte-identically** (behaviour preserved — 16 capability-resolution tests pass). The map is no
  longer aspirational — a provider is wired iff a binding exists — and the builder's coverage
  report makes the gap explicit (runtime 1/6, ci 1/4, vcs 1/4, issue_tracker 3/4, pager 1/3
  wired). "Add a provider = drop a `bindings/<provider>/` folder + rebuild" was demonstrated
  (gitlab→vcs, coverage 1/4→2/4) and reverted. New `CAPABILITY-INDEX` gate (`--check` drift +
  `--strict` BINDING-1: provider in vocabulary, no double-claims). `.mcp.json` files are
  untouched — runtime packaging stays deferred until the A/B/C decision. `conformance: OK`.
- **2026-06-07 — Deprioritized leftovers finished.** (1) **Phase 1 breadth:** rolled
  `routing.yaml` to a wave of 14 artifact/config skills with genuine hard signals (canonical
  doc paths like `docs/architecture/`/`docs/postmortems/`, file-type tokens like `Dockerfile`/
  `EXPLAIN ANALYZE`) — deterministic dispatch now covers **20/149 skills** (general thinking
  skills like `brainstorm`/`explain` correctly stay description-matched: they have no hard
  signal, and the route-hint only narrows on hard signals). +6 ROUTE-TRIGGER fixtures (15
  total), including the `audit-dockerfile`↔`dockerize` path-collision case (both share the
  `Dockerfile` path; the intent breaks the tie both ways); SURFACE-2 uniqueness holds.
  (2) **Phase 5 in-flight checkpoint** (the item previously deferred): implemented at the
  *engine* level rather than via a `PreCompact` hook (cleaner — a hook can't know the run_id):
  `next` stamps `in_flight={step,at,note}`, `complete` clears it, a new `checkpoint` command
  annotates long steps, and SessionStart now shows `mid-step: <step>` on interrupted runs.
  +1 unit test (44 total). Full battery green.
- **2026-06-07 — Phase 3 landed (tools-as-surfaces, Gap 4 "tools added like skills").** Added
  [`shared/schemas/tool.schema.json`](../../shared/schemas/tool.schema.json) + the `tools/<name>/`
  unit (a `tool.json` manifest + an optional `routing.yaml`). `build-surface-index.py` now compiles
  `kind: tool` surfaces and validates every `tool.json` (**TOOL-1**, folded into the SURFACE-INDEX
  gate). The 5 connector `UserPromptSubmit` prompt-detectors were folded into the one registry:
  `jira` / `linear` / `sentry-issue` became routable **tool surfaces** (3 tool units, +3 fixtures →
  18 ROUTE-TRIGGER total). The github PR-URL and pagerduty incident-URL detectors were **deleted as
  subsumed** — `reviewPR` and `respondToIncident` already own those URLs, and re-adding them would
  collide on SURFACE-2 url-uniqueness. The Jira/Linear key ambiguity (identical syntax) is handled by
  scoring: a bare key defaults to jira; a `linear.app` URL + "Linear" wording lets linear (4) outscore
  the shared key shape (3). **The 3rd detection layer's *prompt-detectors* are gone** — all
  *prompt-time* deterministic routing now flows through one builder/table. The 3 `Stop`
  end-of-turn nudges (github suggest-pr / check-recent-ci, snyk check-criticals) **remain by
  design** as event-time instances (Phase 4), so "the bash layer is gone" holds only for the
  prompt-detectors, not the nudges. `conformance: OK`.
- **2026-06-07 — Phase 4 landed (triggering + autonomy, Gaps 2/3).** (1) **Trust axis:** surfaces
  declare `trust` (`propose` | `auto-headless` | `auto`); `build-surface-index` emits it to
  route-signals and `route-hint` surfaces an auto-headless note (originally permissive; **reworded
  2026-06-08** to a non-permissive "declared… still propose-first" after review — see Outcome).
  **TRUST-1** reserves `auto` (it needs a write-scope analysis we don't have
  for skills/tools) — only `propose`/`auto-headless` are permitted; the build fails on `auto`. No real
  surface was flipped (policy is the maintainer's per-surface knob — a one-line routing.yaml change).
  (2) **Arc chaining:** `chainsTo` added to the workflow schema + validator + `ALLOWED_TOP_LEVEL`; the
  engine surfaces it in the completion output (`respondToIncident`→`incidentRetroToActions`,
  `reviewPlan`→`deliberationLoop`); `build-workflow-index --strict` guards dangling targets (verified by
  a typo test); `run-workflow` proposes the next arc, never auto-runs. (3) **Event-time triggering:** a
  polymath-core `PostToolUse` hook (`event-trigger.py`, matcher `Bash`) proposes a surface from *what
  just happened* — a **failed** test run → `bugTriage` — high-precision (requires a test command AND a
  failure marker), quiet/degrade-safe like route-hint (passing runs and non-test "FAILED" stay silent).
  The per-connector `Stop` nudges (github suggest-pr/check-recent-ci, snyk check-criticals) remain as
  connector-specific instances of this same pattern (kept, not deleted). +1 unit test (45 total); 18/18
  ROUTE-TRIGGER; `conformance: OK`. *Honest note:* event-trigger is smoke-tested — there is no committed
  PostToolUse test harness yet (route-hint's scoring is covered by ROUTE-TRIGGER; an event-trigger
  harness is future work).
- **2026-06-07 — Phase 2 packaging completed (Option A, per recommendation).** Implemented the
  A-now / C-capable path production-grade: (1) **Env hardening** — all 8 connector `.mcp.json` files
  now use `${VAR:-}` defaults (22 vars), so an unconfigured provider can't crash MCP config parsing
  (the latent bug the spike surfaced — bare `${VAR}` on `required:false` keys); an unused provider's
  server starts idle and fails its own auth instead of blocking the whole session. (2) **Consistency
  gate** — `BINDING-1` now also verifies each `mcp` binding's `server` exists in the plugin's
  `.mcp.json` and each `userConfigKey` in `plugin.json` `userConfig` (verified: passes today, fires on
  a broken binding), so the binding model and runtime config cannot drift — the seam Option A relies
  on. (3) **Docs** — observability + tracker READMEs (accurate `${VAR:-}` + `/mcp`-disable behaviour),
  `CONNECTOR-POLICY.md` §4.1 (provider configuration & packaging), and the outdated "hand-edit
  `providerPlugins`" step replaced by the binding workflow. Option C (one plugin per provider — the
  only design where *only* the configured provider launches) stays a documented future path the
  binding model already supports; not adopted, to preserve the 51→40 consolidation. `conformance: OK`.

## Outcome (measured)

*Added 2026-06-08, after an adversarial review of the shipped work.* This is the
honest scorecard. Where it disagrees with **Approach / Verification** above, this
section wins.

### Routing — measured, held-out

`tools/route-eval.py` runs 35 held-out prompts (`tests/route-eval/heldout.jsonl`)
through the real `route-hint.py`: naturalistic phrasings, deliberately-signalled
prompts, and adversarial negatives — **none** of them the green-by-construction
ROUTE-TRIGGER fixtures. Result:

| Dimension | Result | Reading |
| --- | --- | --- |
| Precision (signal present → right surface) | **9/9**, 0 misroute, 0 silent-miss | when the hint speaks, it is right |
| False positives (negatives → silent) | **0/7** | acronyms, bare `jira`/`linear`, `RFC 2616`, concept-questions all stay silent |
| Reach (naturalistic prose → fires at all) | **1/16 (~6%)** | the hard-signal floor means natural phrasing rarely triggers a hint |
| Ties (competing surfaces) | both surfaced (≤3); top is table-order-dependent | order is arbitrary on a score tie, but alternatives are *not* hidden |

So the deterministic layer is **trustworthy but low-reach**: correct and quiet,
but on a prompt that doesn't paste a URL/CVE/ticket or type a near-exact
`path`+`intent` phrase, it contributes nothing and the model is back to 1-of-149.
Three silent naturalistic cases even *named* a path token (`Dockerfile`,
`docs/adrs/`, `k8s/`) but lacked the exact intent substring — `intents` are naive
`in`-substring matches, the single biggest reach limiter. Making intents semantic
is the highest-value next lever, but it would require **re-measuring** precision /
false-positives (today's 0-FP rides on exact matching).

### Claim B — the premise — is NOT measured

The motivating premise (*"the model is reliable at 1-of-3 and unreliable at
1-of-131"*) is about **model selection**, which the eval above does not test (it
measures the router, not the model). It needs a live model and is **not runnable
here** (`CLAUDE_CODE_OAUTH_TOKEN` unset; live fixtures disabled,
`LIMITATIONS.md` §4). Procedure to close it:

1. Take ~20 prompts that carry a hard signal (so the hint fires) with a
   known-correct surface.
2. Run each through `claude -p` twice: once normally, once with
   `POLYMATH_ROUTE_MUTE=1` (hint suppressed).
3. Score whether the model invoked/named the correct surface in each arm.
4. The delta (unmuted − muted) **is** the routing layer's value. ≈0 → the hint is
   decorative on artifact-bearing prompts; large → widen reach (semantic intents)
   *with evidence*.

Until that delta exists, the routing layer is justified by precision (it doesn't
mislead) and bounded by reach (it rarely fires) — **not** by a proven selection
lift. This is the one experiment that should gate any further routing investment.

### Connectors (Phase 2) — metadata honest, runtime unchanged

Option A shipped, not the "one server" goal. Bindings + `providerPlugins{}` are
generated and honest (a provider is wired iff a binding exists), and `BINDING-1`
keeps the binding ↔ `.mcp.json` ↔ `plugin.json` triple from drifting. But **all
bundled servers still launch** (an unset provider now fails its own auth instead
of crashing config parse). "Only the configured provider launches" needs Option C
(one plugin per provider) — a deferred maintainer decision that reverses the
51→40 consolidation. Note the binding files *do* duplicate the server name +
`userConfigKeys` that live in `.mcp.json`/`plugin.json`; `BINDING-1` exists to
police that overlap. The bindings earn their keep by adding the
capability→provider vocabulary those files lack, not by removing duplication.

### Autonomy + event-time (Phase 4) — declared, thin, not unified

- **Trust axis:** declared on surfaces, compiled into route-signals, surfaced by
  `route-hint` as a *descriptive* note — but **no executor consumes it and 0
  surfaces are flipped**; `run-workflow` proposes-first for every surface. It is
  forward-looking metadata, not active autonomy. `TRUST-1` does enforce one real
  property: `auto` is forbidden (only `propose` / `auto-headless` compile).
- **Event-time trigger** is a **separate hard-coded `RULES` table** in
  `event-trigger.py` (one rule: failed tests → `bugTriage`), *not* the compiled
  registry. Folding one rule into the registry would be over-engineering;
  unification is worth it only if the rule set grows. It is smoke-tested, with no
  committed PostToolUse harness — below this repo's ROUTE-TRIGGER bar.
- **Arc chaining** (`chainsTo`) ships with two arcs.

### What is unambiguously good

Phase 5 **resumability** is a genuine user-facing fix: a run interrupted
mid-flight (context death / `/clear`) is now surfaced as stale-`active` at
SessionStart instead of going invisible. The **generated `route-signals.json`**
(single producer, replacing a hand-synced copy) and the **honest
`providerPlugins{}`** are real improvements independent of whether routing lifts
selection. The adversarial hardening pass (Jira-acronym false positives, the
fallback-YAML quoted-colon, `${VAR:-}` env defaults) fixed real bugs.

### One-line verdict

Careful, well-gated craft on an **unproven foundation**: the routing layer is
**high-precision / low-reach**, its **selection-lift premise is still unmeasured**,
and several Phase-4 surfaces are **declared, not enforced**. Close Claim B before
widening reach.

## References

- `AGENTS.md` — conformance table, plugin anatomy, workflow architecture.
- `LIMITATIONS.md` — §2 connector philosophy, §4 known gaps.
- `plugins/polymath-core/hooks/scripts/route-hint.py` + `data/route-signals.json`
- `plugins/polymath-flows/bin/polymath-flow` + `data/workflow-detect.json`
- `tools/build-workflow-index.py` (generalize → `build-surface-index.py`)
- `shared/schemas/capabilities.json` + `shared/polymath-profiles.json`
- `docs/CONNECTOR-POLICY.md` — per-connector distinct-value table (`CONNECTOR-2`).
