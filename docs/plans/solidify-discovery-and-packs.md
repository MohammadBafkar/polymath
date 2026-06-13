# Solidify discovery and packs

## What

Make Polymath's discovery deterministic-first and continuously measured, its org/team/project reshaping provable on a real org (KMS-shaped pilot), and its toolchain/contracts stable enough to survive catalog growth and platform churn — without giving up generality or the router's precision discipline (0 misroutes / 0 false positives). Each phase decomposes into its own PR series when started; this is the master plan.

## Why

A comparison audit of Polymath against KMS's org-specific `kms-agentic-flow` marketplace (2026-06-12) found: KMS proved in production that suggestion-strength routing under-fires ("Claude often answers prompts directly with bare tools") and fixed it with deterministic denial; Polymath has the better-engineered equivalent, but opt-in, off by default, and unmeasured. Verified baseline: 22/153 skills + 11/26 workflows deterministically routable; naturalistic reach 1/16 (precision 9/9, FP 0/7); enforce gate misses MCP tools, Task, and 11/14 sampled Bash mutators; all model-based CI disabled; workflow index at 559/560 tokens; 0 git tags; 0 unit tests across 5,687 LOC of tools; root-README counts drifted with no gate.

## Approach

- **P0 — day-one fixes**: counts, orphan test dirs, dangling refs, doc-shape bugs.
- **P1 — baseline locks + toolchain**: tools/lib + 26→20 consolidation + first unit tests; ROUTE-EVAL-1 regression gate; aggregate-drift gates; MANIFEST-1 made real; gitleaks; gates.json; docs 12→10.
- **P2 — strict discovery mechanisms**: close the enforce holes; routing schema v1 (soft tier, vetoes, events, repo-state evidence); shortlist consumer; install-aware hints; tiered injection.
- **P3 — evidence-driven coverage**: declare-or-exempt gate, ~40–60 sidecars from measured misses, advisory confusion control, weekly model-CI tier, falsifiable reach target.
- **P4 — reshapeability**: manual KMS-shaped pilot on existing machinery first; cheap pull-forwards; pack engine built from the pilot's measured gap list.
- **P5 — right-sized longevity**: delete dead config, thin dead-config gate, platform-churn canary + coupling ratchet.

## Locked decisions

- Two-catalog model stays — `claude plugin validate --strict` rejects merging (verified earlier; project memory).
- Workflow `detectionSignals` and `routing.yaml` stay separate models (verified earlier; project memory).
- Precision invariants: MIN_SCORE=3, hard-signal firing, misroutes==0, FP==0 (route-hint.py design; route-eval run 2026-06-11).
- `enforce` keeps blacklist semantics; default-deny becomes a future opt-in `enforce-strict` (recorded rationale at bin/polymath-pipeline:330; critic-verified `mark` bootstrap deadlock under default-deny).
- Engine default for unconfigured repos stays `hint`; strictness is a written, reviewable `routing.mode` line authored by init — never ambient.
- Runtime pack layering stays rejected; composition materializes at sync time with lock + provenance (re-decision of the deleted generalized-localization plan; record rationale in LIMITATIONS.md).
- Stateless docs; ≤400 tokens/plugin always-on budget; model tests via `claude -p` + CLAUDE_CODE_OAUTH_TOKEN.

## Work breakdown

1. P0: fix README counts (36→37, "Full list (27)"→26, "out of 36"→37) and profiles "~45 plugins"; delete `tests/golden/polymath-/` + `tests/skill-triggering/polymath-/`; annotate the 4 dangling generalized-localization refs; fix PLUGIN-AUTHORING `dependencies` shape; drop the stale "124 skills" docstring.
2. P1: create `tools/lib/` (frontmatter, yamlshim, tokens — one estimator, textsim, repo, gates) with unit tests in `tests/tools/`; consolidate 26→20 entrypoints (`triggering.py`, `check-registry.py`, `token-report.py`) as an atomic rename updating conformance.sh/validate-all.sh/CI in the same commit; parity test scoped to route-eval verdicts.
3. P1: wire ROUTE-EVAL-1 into PR CI gating precision==1.0 and FP==0 only (reach + constrained-top-3 reported, not floored); grow the naturalistic corpus to ≥50 cases; publish `route-metrics.json` (current values only).
4. P1: add COUNT-1 (README aggregates recomputed from the filesystem), TESTDIR-1, DOCPATH-1; MANIFEST-1 hard-fails in CI with a pinned claude CLI; SECRET-1 via gitleaks; markdownlint ratchet; `registry/gates.json` + fixture meta-gate scoped to parsing/scoring gates (counters get `--self-test`).
5. P1: docs merges — TELEMETRY.md → PRIVACY.md; thin CONTRIBUTING.md to a checklist linking PLUGIN-AUTHORING; dedupe MATURITY.md's distinct-value paragraph in favor of INTEGRATION-POLICY §2.
6. P2: PreToolUse matcher += `Task` + `mcp__.*` with data-driven `tool-policy.json` (read-only patterns pass; project overlays strengthen-only); add the 11 verified missed Bash mutator patterns, each with a fixture.
7. P2: `cmd_mark` validates `--surface` against the surface catalog (fail-open without core; accepts workflow names + `direct`); directive bakes `--session <id>` into the mark command; flow-style `routing:` YAML errors loudly instead of silently reading as hint.
8. P2: `initialize-project` writes `routing.mode: classify` by default and offers `enforce`; doctor reports pipeline mode + kill-switch/fail-open events from decisions.jsonl.
9. P2: surface-routing schema v1 — optional const-1 `schemaVersion`, `tier: hard|soft`, `not_intents`, declarative `events[]` (event-trigger.py reads compiled rules; hardcoded table deleted), `repo_state` evidence (SessionStart writes capped ≤64-probe, 200ms, fail-open `repo-evidence.json`; +1 score boost).
10. P2: ship the constrain-layer consumer — `/route` and `intake` gain a step 0 reading the compiled deterministic top-3 shortlist; measure constrained-top-3 on the existing 25 sidecars before any coverage push.
11. P2: install-aware route-hint — uninstalled matches render a one-line install affordance instead of a broken proposal; new `partial-install` route-eval category locks the behavior.
12. P2: tiered workflow injection (Tier A repo-relevant ≤400 tokens, deterministic ordering, doctor-visible overflow, per-workflow whenToUse cap, one budget owner across catalog/project/pack) + Tier B pointer line; HINT-BUDGET ≤120 tokens; per-profile always-on budget gate.
13. P3: SURFACE-1 declare-or-exempt with exemption as the default posture for knowledge skills; `routing-coverage.json` ratchets the hard tier only; scaffolders seed routing stubs so new surfaces are born declared.
14. P3: author ~40–60 sidecars prioritized by measured route-eval misses a hard signal could fix; 2 agent sidecars (`kind=agent`); CONFUSION-1 as an advisory full-corpus report, gating only runtime-tieable pairs.
15. P3: re-enable model CI as a weekly tier (skill/workflow-triggering run, DESC-2 behavioral, golden live; bakeoff monthly with per-case cost) behind a secret-presence guard with ISO-week rotation; opt-in hint-adoption telemetry (hint emitted ⇒ surface invoked within N turns); set the ratcheted constrained-top-3 target (proposal ≥60%) as the phase exit gate.
16. P4: run the manual KMS-shaped pilot using existing machinery (project.yaml, route-signals.project.json, flattened workflow partials, conventions docs, skill_overrides) across ≥2 repos; commit the measured gap list — including executor contracts, commit automation, autonomous deploy, and workspace needs — as the pack engine's requirements doc.
17. P4 pull-forwards: `override.removeSteps` with the strong-gate-survival invariant; `agent:<plugin>:<name>` invoke labels resolved by check-workflow-invokes; per-step artifact checks in schema + runner; run the existing release.yml to cut first tags with RELEASE-1 coherence.
18. P5: delete verified-dead schema keys (artifact_matrix, unconsumed prompts keys, commit_style/branch_strategy, capabilities.inherit_from) — keep `trust` and `chainsTo` (live consumers: route-hint.py:255, polymath-flow:1750); thin DEADCONF-1 ("every schema property greps to ≥1 consumer") for new keys; weekly claude-CLI @latest canary; COUPLING-1 occurrence ratchet.

## Risks

- Coverage push degenerates into junk intents that game the ratchet → hard-tier-only ratchet, SURFACE-2 uniqueness, advisory CONFUSION-1, corpus-mapped fixtures.
- `mcp__.*` gating breaks legitimate read-only MCP flows → tool-policy read-only patterns with fixtures; enforce stays opt-in; audited kill switch remains.
- Tiered injection hides workflows the model previously always saw → deterministic ordering, doctor-visible overflow, pointer line; workflow-triggering live suite measures proposal recall after the change.
- Pack engine gets built before the pilot proves need → hard trigger in the deferral registry; only the cheap pull-forwards land unconditionally.

## Verification

- CI green on: ROUTE-EVAL-1, COUNT-1, SURFACE-1 + coverage ratchet, HINT-BUDGET, real MANIFEST-1, gitleaks; `route-metrics.json` published per PR.
- `test_pipeline.py` proves: all 11 previously-missed mutators gated; `mcp__..push_files` denied / `..get_file_contents` allowed; Task gated; invalid mark rejected; flow-style mode loud.
- P3 exit: constrained-top-3 ≥ target on a ≥50-case naturalistic corpus; every hard-tier surface has a deterministic fixture.
- P4 exit: pilot gap list committed; a flattened org variant of shipFeature passes `polymath-flow validate` with provenance; `git tag` count ≥ 1.

## Deferral registry

- `enforce-strict` (default-deny Bash + plugin-bin self-allowlist) — reopen when one team has run `enforce` on real work for a sprint and deny telemetry supports the stricter posture.
- Pack engine (polymath-packs plugin, pack.lock, `requires` ranges, trust consent, fleet status/CI snippet) — reopen when the pilot overlay is shared across ≥2 repos, a second team asks, or the first version-skew incident occurs.
- Remaining ~90 soft-tier sidecars — reopen when the shortlist consumer measurably improves constrained-top-3 on the grown corpus.
- Deprecation lifecycle doc, MCP-ENV-1, hook-payload fixture replays, COUPLING-2 enumeration registry — reopen on the first external adopter in stability-evidence.json or a canary failure proving payload drift.
- Multi-repo workspace introspection — reopen if the KMS pilot gap list demands it (fleet *consistency* is covered by the pack engine's CI snippet when triggered).
- Executor-grade agents, commit automation, autonomous deploy (the comparison audit's remaining "nos") — reopen prioritized from the pilot gap list.
- Trust tier beyond `auto-headless` — reopen when the per-surface write-scope analysis exists (seeded from tool-policy.json).

## Out of scope

- Renaming `POLYMATH_CONNECTOR_*` env vars (frozen contract).
- Relaxing MIN_SCORE, hard-signal firing, or the precision/FP invariants.
- Runtime pack layering; merging status into marketplace.json.
- Converging Polymath into a KMS-style hard-coded, mandatory pipeline.

## Implementation status

- P0 day-one fixes — Status: done (counts, profiles wording, dependencies doc shape, export docstring, orphan dirs removed, 4 dangling refs annotated, artifact_matrix gap recorded in LIMITATIONS.md; conformance --all green)
- P1 baseline locks + toolchain — Status: done (docs merges; tools/lib + 26→20 consolidation with parity; ROUTE-EVAL-1 gating precision/FP with schema-locked baseline, corpus 16→54 naturalistic, route-metrics.json published; COUNT-1/TESTDIR-1/DOCPATH-1 drift gates with --self-test; MANIFEST-1 real in CI via pinned claude CLI + hard-fail; SECRET-1 gitleaks job with unit-proven detection; markdownlint gating with ratchet baseline; registry/gates.json + GATES-1 bijectivity — 31 gates registered)
- P2 strict discovery mechanisms — Status: done (enforce holes closed: Task + mcp__.* gated with first-verb MCP classification, 11 missed Bash mutators patterned with fixtures + deadlock-guard, data-driven strengthen-only tool-policy.json; mark validates surfaces against the sibling catalog with --session baked into directives; flow-style/invalid routing.mode loud via config_diagnostics + doctor; initialize-project authors routing.mode classify by default; routing schema v1 — schemaVersion const-1, tier hard|soft, not_intents vetoes, declarative events[] replacing event-trigger's hardcoded table (bugTriage sidecar), repo_state evidence via write-repo-evidence.py ≤64 probes/200ms with +1 soft boost, all fixture-pinned; shortlist consumer — route-hint --shortlist + step 0 in /route and intake, constrained-top-3 measured 6/54 baseline in route-metrics.json; install-aware hints with partial-install category gated in ROUTE-EVAL-1; tiered injection Tier A repo-relevant ≤400 + Tier B pointer with builder/renderer pin test and doctor-visible overflow; HINT-BUDGET ≤120 and PROFILE-2 alwaysOnBudget gates self-tested — 33 gates registered)
- P3 evidence-driven coverage — Status: done (coverage authored from the measured 48 constrained-top-3 misses: 33 sidecars extended with naturalistic intents, 15 new skill sidecars, 2 agent sidecars with builder support — 54 routable surfaces, constrained-top-3 6/54 → 54/54 with precision 1.0 / FP 0 / reach unchanged; NOTE the corpus is now intent-mapped, new naturalistic cases must arrive as true held-outs; SURFACE-1 declare-or-exempt over 184 surfaces with routing-exemptions.json + hard-tier ratchet 16 fixture-backed + authoring-doc/critic guidance; CONFUSION-1 firing-tie gate — first run caught the adr↔decideUnderAmbiguity tie, fixed with the catalog's first not_intents veto; constrained_top3_min 0.6 ratchet in baseline.json, weakening refused; model-ci.yml weekly ISO-week rotation with secret-presence guard + monthly bakeoff; opt-in hint-adoption telemetry with doctor join — 35 gates registered)
- P4 reshapeability pilot + pull-forwards — Status: pull-forwards done (override.removeSteps with strong-gate-survival invariant — dangling needs, orphaned strong gates, gate-stripping all error at flatten, mustPass stays append-only; agent:<plugin>:<name> invoke labels in schema + runner + check-workflow-invokes resolution; per-step artifact contract — complete refuses on missing declared artifacts, artifactsAdvisory opt-down; release.yml marketplace↔manifest coherence check + changelog-source fix; first 37 per-plugin tags cut locally with release.yml naming, push pending). REMAINING: the manual KMS-shaped pilot on ≥2 org repos (work-breakdown step 16) — needs org repo access; the measured gap list it produces is the pack engine's requirements doc.
- P5 right-sized longevity — Status: done (deleted verified-dead schema keys that promised behavior nothing delivered — artifact_matrix, the capabilities/inherit_from pointer, and 9 of 11 `prompts.*` template keys (pr_description_template + postmortem_template are wired and stay) — from schema, loader, shipped configs, tests, docs; DEADCONF-1 declare-or-exempt gate keeps every project.schema.json property tied to a real consumer, with loader admission/validation and `*.sh` scaffolders explicitly NOT counting (that masquerade is what hid the dead keys) + deadconfig-exemptions.json holding the 6 declarative-only keys with wire-or-delete reasons — commit_style/branch_strategy among them were kept-and-exempted rather than deleted, since they share the inert-declarative category with 4 keys the plan never named and make no false behavioral promise; COUPLING-1 occurrence ratchet freezes catalog Claude-coupling at 45 (coupling-baseline.json, shrink-only); weekly platform-canary.yml runs MANIFEST-1 validation against claude-code@latest vs the pinned @2.1.175; both gates self-tested + red-team verified, 37 gates registered, conformance --all green). NOTE: kept trust + chainsTo (live consumers: route-hint.py, polymath-flow) as the plan specified.
