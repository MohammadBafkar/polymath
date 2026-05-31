# Changelog

All notable changes to this marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Workflow discoverability.** Workflows now carry optional
  `whenToUse` / `triggers` / `detectionSignals` in their YAML
  (`shared/schemas/workflow.schema.json`), and a `polymath-flows`
  SessionStart hook injects a compact routing index — built by
  `tools/build-workflow-index.py` into `plugins/polymath-flows/data/` — so
  the agent can detect a matching workflow from context and propose it
  before running, rather than only running one by name. Adds the
  `reviewPlan` workflow (lightweight plan/design critique), a
  detect → propose → confirm → run contract in the `run-workflow` skill,
  and a `WORKFLOW-INDEX` conformance diff-guard.
- **Project activation path.** Added `polymath-core:initialize-project`
  and `/polymath-core:init-project` to generate
  `.polymath/project.yaml`, `.polymath/capabilities.yaml` when provider
  mappings are known, and `docs/polymath-onboarding.md` from an
  existing repository's README, agent instructions, docs, CI, package
  manifests, and deployment files. Added `activateProject` workflow as
  the flow-runner entry point for the same setup.
- **Iterative deliberation loop.** Added `polymath-thinking:deliberate`,
  `/polymath-thinking:deliberate`, and the `deliberationLoop` workflow
  for observe -> frame -> options -> tradeoffs -> risk critique ->
  revised plan work on plans, designs, documents, implementations, and
  ambiguous problems.
- **Project-context activation metadata.** Extended
  `shared/schemas/project.schema.json` and the SessionStart loader with
  `setup:` and `polymath:` sections for required tools, environment
  variable names, first steps, recommended plugins, recommended
  workflows, and compatible agent surfaces. The Polymath repo now
  dogfoods `.polymath/project.yaml` and `.polymath/capabilities.yaml`.
- **`shared/schemas/polymath-catalog.schema.json`** — JSON Schema
  2020-12 definition for `shared/polymath-catalog.json`, the new
  Polymath-only catalog file. Enforces required fields (`name`,
  `plugins`), allowed status values (`stable` / `beta` /
  `experimental` / `deprecated`), the `polymath-…` plugin-name
  pattern, and rejects unknown extras. Validated in CI via
  `tools/check-catalog.py` when `jsonschema` is on PATH.
- **`tools/check-catalog.py` + `MANIFEST-3` cross-check.** Verifies
  that `.claude-plugin/marketplace.json`, every plugin's `plugin.json`,
  and `shared/polymath-catalog.json` agree on the plugin set and on
  per-plugin versions, independent of whether the Claude CLI is on
  PATH. Catches the same version-drift class of bug that
  `claude plugin validate --strict` catches, plus catalog-set
  divergence (plugin added to marketplace but not catalog, or vice
  versa). Wired into `tools/conformance.sh --all`.
- **Portability adapter to agentskills.io v1.0 harnesses.**
  `tools/export-agents-skills.py` materializes Polymath's 126 skills
  into `dist/agents-skills/<plugin>-<skill>/SKILL.md` with namespaced
  frontmatter `name:` (resolves the one collision in the catalog —
  `file-bug-from-incident` is shipped by both `polymath-connector-jira`
  and `-linear`), copies referenced templates, rewrites
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
  `polymath-connector-github` (added `diagnose-ci-failure`),
  `polymath-core` (added `project-context` plus the SessionStart
  project-yaml loading note), `polymath-devops` (added
  `audit-compose`, `audit-dockerfile` skills and the matching
  commands), `polymath-performance` (added `design-cache-layer`,
  `audit-redis-config` skills and the matching commands),
  `polymath-writing` (added `editorial-pass`).
- **`tools/sync-connector-policy.py`** — generates the
  `connector-policy` disclosure block (`official_surface`,
  `polymath_value`, `sunset_trigger`, `status`) for every
  `polymath-connector-*` and `polymath-infra-*` README from a single
  source: the tables in [`docs/CONNECTOR-POLICY.md`](docs/CONNECTOR-POLICY.md)
  § 3.1–3.2 + `marketplace.json` status. Two modes: `--update`
  (write/rewrite blocks) and `--check` (CI: fail if any README's
  block diverges from the policy table).
- **`tools/conformance.sh CONNECTOR-2` strengthened.** Per-plugin now
  asserts the policy disclosure block is present in each in-scope
  README; the `--all` mode runs the cross-check via
  `tools/sync-connector-policy.py --check` so a policy-table edit
  that's not propagated fails the gate. Resolves the
  `docs/CONNECTOR-POLICY.md § 1` contract drift where 14/14 in-scope
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
  to `polymath-backend` / `polymath-infra-postgres` for schema /
  migration work and to `polymath-ai` for evaluation. `LIMITATIONS.md`
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
  - `polymath-backend:migration-plan` ↔ `polymath-infra-postgres:review-migration`
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
  `plugins/polymath-connector-github/.claude-plugin/plugin.json`
  (declared `0.2.0`) — at install time Claude takes the plugin.json
  version and silently ignores the marketplace entry, so the catalog
  was advertising a stale version; (b) 46 strict-mode warnings from
  Polymath-only fields Claude's schema does not recognize
  (`plugins[N].status`, `metadata.agentSkills`, `metadata.homepage`,
  `metadata.license`). Marketplace entry bumped to `0.2.0` to match
  plugin.json. Polymath-only metadata relocated to a new
  `shared/polymath-catalog.json` (the catalog's own schema, not
  governed by Claude's); `tools/conformance.sh` (MANIFEST-3),
  `tools/build-catalog.py` (status badges on the generated site), and
  `tools/sync-connector-policy.py` (README disclosure block) all read
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
- Capability abstraction (`shared/schemas/capabilities.schema.json`):
  workflows declare *what* they need (issue tracker, observability,
  pager, vulnerability scanner, …) and projects pick the provider once
  in `.polymath/capabilities.yaml`.
- Project localization (`shared/schemas/project.schema.json`):
  `.polymath/project.yaml` describes a project's stack, conventions,
  external skill catalogs, and per-skill overrides; the polymath-core
  SessionStart hook loads it and exposes a resolved snapshot to every
  skill.
- Eleven artifact schemas under `shared/schemas/artifacts/`: `PRD`,
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
- Apache-2.0 license; no telemetry (see [`docs/PRIVACY.md`](docs/PRIVACY.md)).
