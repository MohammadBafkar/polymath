# Changelog

All notable changes to this marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
