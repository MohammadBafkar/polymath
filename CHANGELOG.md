# Changelog

All notable changes to this marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Marketplace bootstrap: marketplace.json, LICENSE (Apache-2.0), shared templates (PRD, User-story-map, CHANGELOG-entry, PR-description, Workflow), workflow JSON schema, scaffolding tools, CI workflows (validate, token-budget, lint, link-check, golden-tests), authoring + workflow + contributing docs.
- Core plugins: polymath-core, polymath-product, polymath-engineering, polymath-release, polymath-flows.
- flows-lite executable (`polymath-flows/bin/polymath-flow`) and `shipFeature` workflow.
- Plugin maturity tiers — every plugin entry in `.claude-plugin/marketplace.json` now declares `status: stable | beta | experimental | deprecated`. Source of truth is `marketplace.json` (not `plugin.json`) because Claude Code's `plugin validate --strict` rejects any unknown top-level field in `plugin.json`. New `MANIFEST-3` conformance criterion enforces presence + validity. Catalog pages and `marketplace.json` surface the tier as a badge. Initial assignment: 8 stable (polymath-core, -thinking, -planning, -writing, -decisions, -engineering, -flows, -author); 63 experimental (everything else, including all `polymath-connector-*`, `polymath-lang-*`, and `polymath-infra-*`). Documented in [docs/PLUGIN-AUTHORING.md § 3.1](docs/PLUGIN-AUTHORING.md). Promotion to `stable` requires a strong-gated workflow + a live-model golden fixture + at least one external user.
- Agent governance reversal — the rule "no custom agents in MVP unless a golden fixture proves they outperform a skill" was structurally rigged: a skill in the parent context can never lose on tokens, so an agent could not earn its place even when it should. New rule: a new agent must ship with a golden fixture showing it finds something a **no-agent baseline** misses (same input, same Claude lead, no subagent). The fixture trace + no-agent trace are both checked in. Updated in [docs/PLUGIN-AUTHORING.md § 6](docs/PLUGIN-AUTHORING.md).
- Workflow gate hardening — round 2:
  - All 13 previously weak-gated workflows now declare a strong-deterministic blocking gate. Pattern by workflow: PRD-shaped (`featureFromIdea`) gets `artifactSchemaStrict` on the PRD + `diffConstraint` on implementation; doc-producing workflows (`bugTriage`, `experimentToGA`, `incidentRetroToActions`, `reviewPR`, `weeklyReleaseTrain`) get `diffConstraint` with `pathAllowlist` constraining the workflow's effect to its docs lanes; code-changing workflows (`bumpDependency`, `migrateLanguageVersion`, `refactorWithSafety`, `sunsetCapability`, `securityFinding`, `perfRegression`, `deprecationToRemoval`) get `diffConstraint` with `filesChanged.min/max` and `linesChanged.max` bounds, plus `pathBlocklist` on `.git/**`. Existing `stepSummaryMatches` checks demoted to `severity: advisory`. `polymath-flow validate` no longer warns on any bundled workflow.
  - **Fallback YAML parser** in `polymath-flow` now folds `|` and `>` block scalars (treating both as folded — newlines→spaces). Previously the fallback parser silently lost the `mustPass` section of any workflow that used `prompt: |` for multi-line prompts (e.g. `deprecationToRemoval.yaml`), which made the strong-gate warning hide real gaps.
- Workflow gate hardening (v0.2 of the mustPass contract):
  - New `artifactSchemaStrict` mustPass check — validates artifact frontmatter against the full schema, rejects extra fields by default, and requires a configurable `minBodyChars` of substantive (non-heading, non-whitespace) body content. Catches hollow stub artifacts (e.g. `# PRD\n`) that the existing `fileExists` and `artifactValid` checks let pass.
  - New `diffConstraint` mustPass check — bounds the workflow's effect on the working tree (or a ranged git diff): `filesChanged.min` / `.max`, `linesChanged.min` / `.max`, `pathAllowlist`, `pathBlocklist`, optional `since` ref. Untracked files are counted.
  - New `severity:` field on every check — `advisory` checks run and report but do not pause the workflow on failure; `blocking` checks (the default) halt the run. `stepSummaryMatches` is now advisory by default — a regex match on a freeform summary string can no longer pass a workflow on its own.
  - `polymath-flow validate` now emits a warning (non-fatal) when a workflow has no strong-deterministic blocking mustPass check (`commandSucceeds`, `artifactValid`, `artifactSchemaStrict`, or `diffConstraint`). 13 of the 15 bundled workflows currently emit this warning and are queued for migration.
  - `shipFeature.yaml` migrated to the new contract: `tests-mentioned` demoted to advisory; new blocking gates `prd-strict` (artifactSchemaStrict, minBodyChars=200) and `implement-produced-diff` (diffConstraint, filesChanged.min=1, max=200, linesChanged.max=5000, pathBlocklist `.git/**`).
  - **Falsifiability anchor**: a new CI job (`falsifiability-anchor` in `golden-tests.yml`) and unit test (`test_hollow_run_blocked_by_strong_gates`) deliberately drive a hollow shipFeature run (empty PRD stub, no source change, summaries that match the weak regex) and assert it is BLOCKED. The day this anchor passes is the day a strong gate has regressed.

### Fixed

- Two workflows that PyYAML strict-parsed as invalid have been rewritten:
  - `incidentRetroToActions.yaml` — step prompt with embedded `For each:` colon refactored to remove the YAML mapping ambiguity.
  - `weeklyReleaseTrain.yaml` — `dryRun` input description rewritten so the leading single-quoted token no longer breaks the scalar; `values: [yes, no]` quoted to `["yes", "no"]` so PyYAML does not coerce them to booleans.
- `reviewPR.yaml` input renamed `diff_path` → `diffPath` to satisfy the schema's camelCase requirement (was silently rejected by strict CI validation but accepted by the lenient fallback parser).
