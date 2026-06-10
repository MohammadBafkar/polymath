# Changelog

All notable changes to this marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Defaults packs (one-command scope localization).**
  `polymath-author:/new-pack` scaffolds a standalone marketplace of
  per-scope conventions plugins — organization, team, product line, or
  project archetype — each with an `apply-defaults` copy-in skill, starter
  `.polymath/` config + role map, and a conventions corpus seeded from
  the polymath-core skeletons; re-running against an existing pack adds a
  scope plugin (narrowest scope applies first; copy-in never overwrites).
  `init-project` detects installed packs (the `apply-defaults` skill-name
  convention), proposes their copy-in first, offers to scaffold
  `.polymath/conventions/` from the templates, and registers docs in
  `conventions_docs` by role.
- **Convention packs (content layer).** Skeleton templates under
  `plugins/polymath-core/templates/conventions/` (knowledge-base, stack-doc,
  artifact-matrix, review-checklist) with the `[VERIFY: …]` marker protocol;
  nine skills now consume project localization — seven read
  `conventions_docs` by role (code-review, verify-change, feature-dev,
  api-design-rest, db-schema, dockerize, ci-pipeline-github), two use
  `prompts` templates (pr, postmortem-blameless). The consumption contract
  lives in `polymath-core:project-context`, which now resolves the snapshot
  by glob across the namespaced plugin data dirs.
- **`${project.*}` workflow placeholders.** flows-lite steps and gates can
  reference the project-context snapshot
  (`${project.stack.languages.0.lang}`), frozen into run state at `start`.
  The `${project.<path>:-fallback}` form degrades for repos with no
  `.polymath/project.yaml`; `polymath-flow validate` warns on the bare
  form, which is reserved for project/org-layer workflows.
- **Localization keys in the project schema** — shipped ahead of their
  consumers per `docs/plans/generalized-localization.md`: `conventions_docs`
  (convention docs resolved by role), `smoke` (per-language
  boot-verification recipes), `tracker` (work-item destination +
  provenance marking), `routing.mode` (`hint`/`classify`/`enforce`;
  only `hint` has shipped behavior), `attribution`, `artifact_matrix`,
  and `prompts` opened to the full 11-artifact template vocabulary.
  Validated by schema + loader; consumers land in later plan phases.
- **Machine-local project-config overlay.** `./.polymath/project.local.yaml`
  (gitignored) deep-merges on top of the resolved `project.yaml` — mappings
  merge per key with the overlay winning, lists and scalars replace. The
  overlay is fail-open (warned and skipped on any problem) and may serve as
  the sole source when no base file resolves. First step of the
  generalized-localization plan (`docs/plans/generalized-localization.md`).

### Changed

- **Project-config loader tolerates unknown top-level keys.** Unknown keys
  in `project.yaml` are warned and dropped (recorded in
  `_meta.ignored_keys`) instead of failing the session with exit 2 — so a
  config written for a newer schema degrades gracefully on an older
  polymath-core. A drift-gate test pins the loader's key whitelist to
  `registry/schemas/project.schema.json`.

- **Stateless docs.** Documentation describes current behaviour only —
  change narration, "as of" dates, and point-in-time snapshots are removed;
  git history and this changelog are the records of evolution. Deleted
  `docs/STABILITY-ROADMAP.md` (hand-reconciled ledger snapshot + iteration
  plan) and `docs/QUALITY-DASHBOARD.md`: the evidence ladder and
  ledger-update procedure now live in `docs/MATURITY.md`, measurement and
  artifact locations in `docs/QUALITY-SCORECARD.md`. Promotion bars are
  stated once, in MATURITY — the scorecard's paraphrase had drifted from
  the canonical text — and the scorecard's gate list now matches what CI
  actually runs (per-PR gates vs `main`-push and opt-in live runs).

- **Concept/capability-centric plugins (breaking — published names change).**
  Integration plugins are now named by the capability they serve, with vendors
  as interchangeable providers underneath:
  `polymath-vcs`, `polymath-tracker`, `polymath-paging`, `polymath-chat`, and
  `polymath-vuln-scan`, plus infra `polymath-cloud` / `polymath-kubernetes`. The
  observability design discipline absorbed the observability vendor integration,
  so `polymath-observability` holds both the RED/USE design skills and the
  Datadog/Grafana/Honeycomb/Elastic/Sentry query integration. Integration/infra
  conformance gates detect by `.mcp.json`/`bindings/` rather than name prefix.
  Additional vendors per concept (GitLab, Azure DevOps, Teams, Opsgenie, …) are
  listed in the capability vocabulary as the roadmap and wired when a real MCP
  package ships. The previous vendor-named plugins were renamed or merged into
  the above — the old→new mapping is in git history.
- **Consolidation: 51 → 36 plugins (no skills lost).** Folded single-skill and
  thin fragments into their parent craft, and merged per-vendor integrations by
  capability, to cut install decisions and confusable descriptions:
  - **Costume connector:** a CLI-only Terraform `plan-review` skill (no MCP
    server or binding) → `polymath-cloud`, with the IaC design skills.
  - **Fragments:** `polymath-finops:cloud-cost-review` → `polymath-cloud`;
    `polymath-prioritize:prioritize` → `polymath-planning`;
    `polymath-product-strategy:product-strategy` → `polymath-product`;
    `polymath-supply-chain:supply-chain-review` → `polymath-security`;
    `polymath-i18n:i18n-audit` → `polymath-frontend`.
  - **Data tier:** Postgres migration skills (`review-migration`,
    `audit-pg-config` + commands) → `polymath-backend`, next to
    `db-schema`/`migration-plan`.
  - **Comms:** `polymath-content` (`write-release-notes`, `write-advisory`,
    `write-sunset-notice`) → `polymath-communication`.
  - **Delivery:** `polymath-progressive-delivery` (`safe-rollout`) and
    `polymath-deprecation` (`deprecation-plan`, `migration-guide`) →
    `polymath-release`, which now spans commit → rollout → sunset.
  - **Integrations by capability:** Jira + Linear → **`polymath-tracker`** (one
    `issue_tracker` umbrella; both MCP servers; the colliding
    `file-bug-from-incident` unified into one provider-agnostic skill). Datadog +
    Grafana/Honeycomb/Elastic → **`polymath-observability`** (closes a latent
    `query-during-incident` resolution gap). The capability vocabulary
    (`registry/schemas/capabilities.json`) maps those providers to the umbrella
    plugins.

  Skill bodies, commands, golden fixtures, skill-triggering tests, and workflow
  `invoke:`/`requires.plugins` refs moved with each skill; only the
  `plugin:skill` prefix changed. The standalone fragment/vendor plugins are
  removed from the marketplace. Fragment/delivery/comms merges used
  absorb-into-incumbent (preserving the `polymath-release`/`polymath-communication`
  names and their workflow refs) rather than the doc's aspirational
  `polymath-delivery`/`polymath-comms` rename — lower-risk, same consolidation.

### Removed

- **`mcp_servers` key in `project.yaml`.** It was declared in the schema but
  consumed by nothing; capability → provider/plugin selection is owned by
  `.polymath/capabilities.yaml` and duplicating that ownership invited
  drift. Files still declaring it get a warning and the key is ignored.

### Added

- **Install profiles (discovery Layer 1).** `registry/polymath-profiles.json`
  defines seven curated role spines (`backend`, `frontend`, `sre`, `platform`,
  `pm`, `staff`, `author`) so a new user picks one profile instead of choosing
  from ~45 plugins, then installs more a-la-carte. Validated by
  `tools/check-profiles.py` (`PROFILE-1` in `conformance.sh --all`) so a
  fold/rename can never leave a dangling profile reference. Documented in the
  README quick-start. **Layer 2:** `initialize-project` now starts its
  recommended-install set from the closest profile and emits the install
  command.

- **Lead with journeys.** The README opens with a journeys table, and
  `tools/build-catalog.py` renders a data-driven journeys section atop the
  generated site (above plugins-by-tier) — the workflow is the unit of value;
  plugins are the ingredients.

- **Ambient routing (pull → push).** `polymath-core` gained a
  `UserPromptSubmit` hook that extracts deterministic signals from a prompt
  (URLs, CVE/GHSA keys, mentioned paths, inline diffs, intent phrasings),
  scores them against a bundled signal table, and proposes the smallest
  matching Polymath surface in one quiet line — only when a *hard* signal is
  present, never auto-running. New `tools/route-triggering.py` makes routing
  precision a deterministic, model-free CI gate (`ROUTE-TRIGGER` in
  `conformance.sh --all`).
- **Workflow-first routing surface.** Added `polymath-core:route` and
  `/polymath-core:route` to choose the right workflow, skill, connector,
  agent, or external catalog for a prompt before doing work. The router
  returns JSON with confidence, evidence, alternatives, a clarifying
  question when needed, and the next action. Added skill-triggering and
  golden fixtures, and refreshed the README's marketplace counts.

- **Four composed workflow arcs** in `polymath-flows`: `prdToShip`,
  `estimateAndPlan`, `requirementsToBacklog`, and `progressiveRollout` —
  right-sized arcs the audit flagged as missing, now composable from the
  gap-closure skills. Each carries routing metadata and a workflow-triggering
  test; the injected-index ceiling was recalibrated to 560 (last flat-surface
  bump before tiering at ~30). A fifth, `incidentToReview`, was dropped before
  release as a duplicate of the `respondToIncident → incidentRetroToActions`
  chain; its trigger phrasings moved onto `respondToIncident`.

- **`polymath-i18n` plugin (experimental).** `i18n-audit` — assess
  internationalization readiness (hardcoded strings, locale formatting, ICU
  plurals, text expansion, RTL/bidi, fallback chain, pseudolocalization in CI).
  Closes the one SDLC phase the audit found with zero coverage.
- **`polymath-supply-chain` plugin (experimental).** `supply-chain-review` —
  SBOM, dependency provenance/lockfiles, license audit, build-pipeline trust,
  signing/SLSA attestation, and compliance-control mapping (distinct from
  runtime CVE triage).
- **`polymath-product-strategy` plugin (experimental).** `product-strategy` —
  vision, ICP/segmentation, positioning, pricing/packaging, moat, and GTM as
  explicit choices with testable assumptions.
- **`polymath-planning:forecast` skill.** Probabilistic delivery forecasting
  (reference-class, throughput/Monte-Carlo, cone of uncertainty), distinct from
  the per-item three-point `estimate`.

- **`polymath-deprecation` plugin (experimental).** `deprecation-plan`
  (two dates, telemetry-gated removal, comms cadence, exception path,
  in-product markers) and `migration-guide` (consumer before/after upgrade
  steps with rollback) — the planning + consumer-migration half of
  deprecation that the sunset notice/workflows didn't cover.
- **`polymath-finops` plugin (experimental).** `cloud-cost-review` —
  attribute cloud spend, find waste, rightsize, compute unit economics, assess
  commitment coverage, and propose a budget + anomaly alert (real cloud cost,
  distinct from internal token budgeting).
- **Ideation skills in `polymath-thinking`.** `problem-framing` (frame the
  problem before any solution) and `first-principles` (decompose to bedrock,
  drop inherited assumptions) — closing the front-of-SDLC ideation gap.

- **`polymath-progressive-delivery` plugin (experimental).** Closes the
  delivery-safety P1 gap: the `safe-rollout` skill designs a progressive
  rollout — feature-flag strategy, canary/blue-green/ring stages with bake
  times, SLO-driven health gates, automated rollback, and a kill switch —
  and flags irreversible data changes a flag can't undo.
- **`polymath-test-automation` plugin (experimental).** Closes the
  test-automation P1 gap with two skills: `e2e-flow` (browser end-to-end
  for a critical journey — stable selectors, web-first waits, deterministic
  data) and `load-test` (load/stress/soak with a realistic workload model
  and percentile pass/fail thresholds). Both ship golden fixtures and
  skill-triggering tests.

- **QA depth (P0 gap closure).** Added three skills to `polymath-qa`:
  `test-smell` (suite anti-pattern review), `integration-contract`
  (service-boundary + consumer-driven contract tests), and
  `assertion-quality` (assert behavior, not implementation).
- **Product roadmapping/grooming (P0 gap closure).** Added `roadmap`
  (Now/Next/Later by outcome) and `groom-backlog` (Definition-of-Ready
  refinement) to `polymath-product`. Each new skill ships a skill-triggering
  test with forbidden-prompt boundaries against its siblings.

- **`polymath-prioritize` plugin (experimental).** Closes the top SDLC gap
  from the catalog audit: ranking a backlog with an explicit, inspectable
  method. The `prioritize` skill supports RICE, WSJF/cost-of-delay, MoSCoW,
  Kano, and value-vs-effort, picks the lightest method the signals support,
  shows the inputs behind every score (never an opaque number), surfaces
  confidence, and cuts a Now/Next/Later roadmap to `docs/prioritization/<slug>.md`.
  Ships with a golden fixture and a skill-triggering test; registered in both
  catalogs at `experimental`.

- **Description-quality linter.** `tools/lint-descriptions.py` scores every
  always-on description (skill / command / agent) on trigger clarity, scope
  boundary, and disambiguation. The `DESC-1` conformance gate
  (`--strict`) blocks any two descriptions that token-collide without a
  distinguishing proper noun, so a router can always tell siblings apart;
  scope-boundary coverage is reported as an advisory backlog. Rewrote the
  scaffolder (`new-plugin`/`new-skill`/`new-command`/`new-connector`) and
  alias (`init-project`, `review-migration`, `audit-redis-config`) command
  descriptions to clear the existing collisions.
- **Confusion-matrix gate.** `tools/check-description-confusion.py` +
  `tests/forbidden_prompts.yaml` encode the audit's sibling-routing clusters
  (issue triage, caching, decompose, test ownership, perf budgets, critique,
  docs). The `DESC-2` gate validates the cases structurally; the behavioural
  `run` mode (naive prompt must load the expected skill, never a forbidden
  sibling) is opt-in under `CLAUDE_CODE_OAUTH_TOKEN`.
- **Scope-boundary clauses on the confusion clusters.** Added explicit "Not
  for X / use Y" boundaries to ~20 sibling skills the audit flagged as
  confusable (issue triage, caching, decompose, test ownership, perf budgets,
  critique, docs), so each names where it ends. Leading trigger text is
  preserved; all stay within the per-plugin token budget.

- **Workflow discoverability.** Workflows now carry optional
  `whenToUse` / `triggers` / `detectionSignals` in their YAML
  (`registry/schemas/workflow.schema.json`), and a `polymath-flows`
  SessionStart hook injects a compact routing index — built by
  `tools/build-workflow-index.py` into `plugins/polymath-flows/data/` — so
  the agent can detect a matching workflow from context and propose it
  before running, rather than only running one by name. Adds the
  `reviewPlan` workflow (lightweight plan/design critique), a
  detect → propose → confirm → run contract in the `run-workflow` skill,
  and `WORKFLOW-INDEX` + `WORKFLOW-2` + `WORKFLOW-TRIGGER` conformance gates
  (`WORKFLOW-2` requires `whenToUse`/`triggers` on every workflow with
  globally-unique triggers). Adds
  `tools/workflow-triggering.py` and `tests/workflow-triggering/*.md` — the
  workflow analogue of skill-triggering: a naive prompt must make the model
  propose the right workflow (`check` in CI; `run` opt-in under
  `CLAUDE_CODE_OAUTH_TOKEN`).
- **Project activation path.** Added `polymath-core:initialize-project`
  and `/polymath-core:init-project` to generate
  `.polymath/project.yaml`, `.polymath/capabilities.yaml` when provider
  mappings are known, and `docs/POLYMATH-ONBOARDING.md` from an
  existing repository's README, agent instructions, docs, CI, package
  manifests, and deployment files. Added `activateProject` workflow as
  the flow-runner entry point for the same setup.
- **Iterative deliberation loop.** Added `polymath-thinking:deliberate`,
  `/polymath-thinking:deliberate`, and the `deliberationLoop` workflow
  for observe -> frame -> options -> tradeoffs -> risk critique ->
  revised plan work on plans, designs, documents, implementations, and
  ambiguous problems.
- **Project-context activation metadata.** Extended
  `registry/schemas/project.schema.json` and the SessionStart loader with
  `setup:` and `polymath:` sections for required tools, environment
  variable names, first steps, recommended plugins, recommended
  workflows, and compatible agent surfaces. The Polymath repo now
  dogfoods `.polymath/project.yaml` and `.polymath/capabilities.yaml`.
- **`registry/schemas/polymath-catalog.schema.json`** — JSON Schema
  2020-12 definition for `registry/polymath-catalog.json`, the new
  Polymath-only catalog file. Enforces required fields (`name`,
  `plugins`), allowed status values (`stable` / `beta` /
  `experimental` / `deprecated`), the `polymath-…` plugin-name
  pattern, and rejects unknown extras. Validated in CI via
  `tools/check-catalog.py` when `jsonschema` is on PATH.
- **`tools/check-catalog.py` + `MANIFEST-3` cross-check.** Verifies
  that `.claude-plugin/marketplace.json`, every plugin's `plugin.json`,
  and `registry/polymath-catalog.json` agree on the plugin set and on
  per-plugin versions, independent of whether the Claude CLI is on
  PATH. Catches the same version-drift class of bug that
  `claude plugin validate --strict` catches, plus catalog-set
  divergence (plugin added to marketplace but not catalog, or vice
  versa). Wired into `tools/conformance.sh --all`.
- **Portability adapter to agentskills.io v1.0 harnesses.**
  `tools/export-agents-skills.py` materializes Polymath's 126 skills
  into `dist/agents-skills/<plugin>-<skill>/SKILL.md` with namespaced
  frontmatter `name:` (which resolves any name collision in the
  catalog), copies referenced templates, rewrites
  `../../templates/X.md` links, and emits a `manifest.json` mapping
  back to source `<plugin>:<skill>`. New `docs/PORTABILITY.md`
  documents the per-harness drop directory (Codex CLI, Cursor,
  GitHub Copilot, VS Code, Gemini CLI, Goose, JetBrains Junie) and
  is explicit about what does NOT port (commands, hooks, MCP config,
  workflows, agents, artifact schemas, project-localization). The
  `dist/` output is gitignored.
- **`tools/check-readme-inventory.py` + `DOCS-2` conformance check.**
  Asserts every plugin's `README.md` mentions every shipped
  first-class surface (skill, command, agent, `bin/` executable) by
  name. Catches the systemic drift where a `README` "What it ships"
  list lags the directory after a new skill or command lands.
  `tools/conformance.sh --all` now runs this check after the
  per-plugin pass. Fixed 15 drifts across 6 plugins: `polymath-author`
  (new `new-command`, `new-workflow`, five `bin/` scaffolders),
  `polymath-vcs` (added `diagnose-ci-failure`),
  `polymath-core` (added `project-context` plus the SessionStart
  project-yaml loading note), `polymath-devops` (added
  `audit-compose`, `audit-dockerfile` skills and the matching
  commands), `polymath-performance` (added `design-cache-layer`,
  `audit-redis-config` skills and the matching commands),
  `polymath-writing` (added `editorial-pass`).
- **`tools/sync-integration-policy.py`** — generates the
  integration-policy disclosure block (`official_surface`,
  `polymath_value`, `sunset_trigger`, `status`) for every integration &
  infra plugin README from a single
  source: the tables in [`docs/INTEGRATION-POLICY.md`](docs/INTEGRATION-POLICY.md)
  § 3.1–3.2 + `marketplace.json` status. Two modes: `--update`
  (write/rewrite blocks) and `--check` (CI: fail if any README's
  block diverges from the policy table).
- **`tools/conformance.sh INTEGRATION-2` strengthened.** Per-plugin now
  asserts the policy disclosure block is present in each in-scope
  README; the `--all` mode runs the cross-check via
  `tools/sync-integration-policy.py --check` so a policy-table edit
  that's not propagated fails the gate. Resolves the
  `docs/INTEGRATION-POLICY.md § 1` contract drift where 14/14 in-scope
  READMEs previously violated the disclosure mandate.

### Changed

- **Maturity tiers reconciled.** Tier definitions and promotion bars
  consolidated into a single source of truth at
  [`docs/MATURITY.md`](docs/MATURITY.md). Previously, the `beta` bar was
  defined three times across `LIMITATIONS.md`, `docs/PLUGIN-AUTHORING.md`
  § 3.1, and `docs/QUALITY-SCORECARD.md`, with conflicting wording. The
  canonical rule:
  - `experimental` — structural + ≥ 1 golden fixture.
  - `beta` — on-disk evidence loop closed (bakeoff + triggering tests
    for skill-shaped plugins; ≥ 20 unit-test assertions + an
    end-to-end job for foundation-runner plugins). Live LLM runs not
    required.
  - `stable` — live bakeoff ≥ 8 / delta ≥ 2 + at least one external
    adopter beyond the maintainer.
- **Marketplace statuses updated under the canonical rule.**
  - `polymath-incident` → `beta` (bakeoff: `postmortem-blameless`; triggering: `postmortem-blameless`).
  - `polymath-product` → `beta` (bakeoff: `feature-from-idea-rate-limit`; triggering: `prd`).
  - `polymath-security` → `beta` (bakeoff: `owasp-review`; triggering: `stride-threat-model`).
  - `polymath-sre` → `beta` (bakeoff: `slo-design`; triggering: `slo-design`).
  - `polymath-decisions` → `experimental` (golden fixture only; lacks bakeoff + triggering — to be re-promoted once fixtures land).
- **`polymath-data` scope clarified and narrowed.** README now lists
  all four skills (was: omitted `run-experiment`), declares the
  intentional narrow scope (SQL + metrics + experiments), and points
  to `polymath-backend` for schema / migration work and to
  `polymath-ai` for evaluation. `LIMITATIONS.md`
  § 3 records the deferral of data-engineering and data-science
  surfaces.
- **`sql-optimize` deepened to multi-dialect EXPLAIN reading.** New
  per-dialect cheat sheet for Postgres, MySQL ≥ 8, SQLite, BigQuery,
  Snowflake, Redshift, DuckDB; clarifies the read-direction rule
  (Postgres bottom-up, MySQL / BigQuery / Snowflake top-down) and adds
  the "fix storage layout before SQL on warehouse engines" anti-pattern.
- **Cross-links added to duplicate-feeling skill pairs.** Pairs are
  kept separate (different layer or audience) and cross-link instead
  of merging — per Codex critique of the original review plan:
  - `polymath-performance:caching-tradeoffs` ↔ `:design-cache-layer`
    (strategy ↔ Redis implementation), with both linking
    `:audit-redis-config`.
  - `polymath-release:release-notes` ↔ `polymath-content:write-release-notes`
    (engineer ↔ customer audience), both linking `polymath-release:changelog`.
  - `polymath-backend:migration-plan` ↔ `polymath-backend:review-migration`
    (vendor-agnostic phasing ↔ Postgres statement review).
- **GitHub Actions hygiene.** Added explicit `permissions:` (least
  privilege, default `contents: read`) and `concurrency:` (cancel
  in-progress on the same PR / ref) to `validate.yml`, `lint.yml`,
  `link-check.yml`, `token-budget.yml`, `golden-tests.yml`.
- **`token-budget` PR comment is now sticky.** Replaces the
  spam-on-every-push behaviour with an upserted comment keyed by a
  `<!-- polymath:token-budget -->` marker.
- **Claude Code CLI install simplified.** `golden-tests.yml` and
  `evaluation.yml` now install via `npm install -g @anthropic-ai/claude-code`
  only — dropped the curl-installer fallback which was duplicative.

### Fixed

- **`claude plugin validate --strict .` now passes at the marketplace
  root.** Two real problems were silently in place: (a) a version drift
  between `.claude-plugin/marketplace.json` (declared `0.1.0`) and
  `plugins/polymath-vcs/.claude-plugin/plugin.json`
  (declared `0.2.0`) — at install time Claude takes the plugin.json
  version and silently ignores the marketplace entry, so the catalog
  was advertising a stale version; (b) 46 strict-mode warnings from
  Polymath-only fields Claude's schema does not recognize
  (`plugins[N].status`, `metadata.agentSkills`, `metadata.homepage`,
  `metadata.license`). Marketplace entry bumped to `0.2.0` to match
  plugin.json. Polymath-only metadata relocated to a new
  `registry/polymath-catalog.json` (the catalog's own schema, not
  governed by Claude's); `tools/conformance.sh` (MANIFEST-3),
  `tools/build-catalog.py` (status badges on the generated site), and
  `tools/sync-integration-policy.py` (README disclosure block) all read
  status from there. `tools/validate-all.sh` now invokes
  `claude plugin validate --strict` at the marketplace root and fails
  on non-zero exit, so any future drift is caught in CI before merge.
  `README.md`, `AGENTS.md`, `docs/PLUGIN-AUTHORING.md`, and
  `docs/MATURITY.md` updated to point at the new catalog location.
- **`tools/export-agents-skills.py` no longer crashes when `--out`
  points outside the repository.** The success-message line was
  unconditionally calling `Path.relative_to(REPO)`, which raised
  `ValueError` for absolute paths like `/tmp/skills` even though the
  export itself had already completed. Now falls back to printing the
  absolute path when the output directory is outside the repo.

### Security

- **`.github/workflows/claude.yml` `@claude` mentions now require a
  trusted author.** The job's `if:` condition was previously
  `contains(comment.body, '@claude')` alone — any GitHub user
  commenting on any issue or PR could trigger a paid Claude run
  backed by `secrets.CLAUDE_CODE_OAUTH_TOKEN`. Added an
  `author_association` gate to each branch (issue_comment,
  pull_request_review_comment, pull_request_review, issues), matching
  the pattern already in `evaluation.yml`: OWNER, MEMBER, or
  COLLABORATOR only. Also added `timeout-minutes: 30` to bound runaway
  runs.
- **`/evaluate` is gated by `author_association`.** The
  `live-bakeoff` job in
  [`.github/workflows/evaluation.yml`](.github/workflows/evaluation.yml.disabled)
  now refuses to run on `issue_comment` events unless the commenter is
  `OWNER`, `MEMBER`, or `COLLABORATOR`. Drive-by PR comments from forks
  can no longer trigger secret-bearing steps.

## [0.1.0]

### Added

- First public release of the Polymath marketplace. 43 plugins across
  foundation, mind & craft, product & discovery, engineering, quality
  & safety, platform & operate, infra, people & content, connectors,
  orchestration, and authoring. 15 workflows orchestrating those
  plugins into SDLC scenarios.
- Capability abstraction (`registry/schemas/capabilities.schema.json`):
  workflows declare *what* they need (issue tracker, observability,
  pager, vulnerability scanner, …) and projects pick the provider once
  in `.polymath/capabilities.yaml`.
- Project localization (`registry/schemas/project.schema.json`):
  `.polymath/project.yaml` describes a project's stack, conventions,
  external skill catalogs, and per-skill overrides; the polymath-core
  SessionStart hook loads it and exposes a resolved snapshot to every
  skill.
- Eleven artifact schemas under `registry/schemas/artifacts/`: `PRD`,
  `ADR`, `Plan`, `RFC`, `Runbook`, `ArchitectureDoc`, `DACIDecision`,
  `TradeoffMatrix`, `Postmortem`, `ThreatModel`, `PRDescription`.
  Workflows enforce frontmatter discipline via `mustPass:
  artifactValid` and `artifactSchemaStrict`.
- Deterministic workflow runner at
  `plugins/polymath-flows/bin/polymath-flow` with `mustPass` types:
  `fileExists`, `fileMatches`, `commandSucceeds`,
  `stepSummaryMatches`, `command`, `artifactValid`,
  `artifactSchemaStrict`, `diffConstraint`. Each check has optional
  `severity: advisory | blocking`.
- Bakeoff harness at `tools/bakeoff.py` with regex pre-filter +
  optional LLM-judge scoring (`--judge`). Nine pre-registered cases
  under `tests/bakeoff/<plugin>/<scenario>/case.json`. Symmetric-prompt
  contract enforced by `bakeoff check`.
- Skill-triggering tests at `tests/skill-triggering/<plugin>/<skill>.md`
  with a runner (`tools/skill-triggering.py`) that exercises naive
  user prompts via `claude -p --output-format stream-json`.
- Token-usage analyzer at `tools/analyze-token-usage.py` for
  per-subagent / per-skill / per-tool token breakdowns.
- agentskills.io v1.0 conformance declaration in
  `.claude-plugin/marketplace.json` `metadata.agentSkills`.
- CI gates: `tools/conformance.sh --all`, `tools/lint-skills.sh`,
  `tools/token-budget.sh`, `tools/build-catalog.py --check`,
  `polymath-flow validate`, `tools/bakeoff.py check`,
  `tools/skill-triggering.py check`, the workflow runner's unit tests,
  and the polymath-core project-context loader's unit tests.
- `/evaluate` PR slash command + nightly scheduled bakeoff in
  `.github/workflows/evaluation.yml`.
- MIT license; no telemetry (see [`docs/PRIVACY.md`](docs/PRIVACY.md)).
