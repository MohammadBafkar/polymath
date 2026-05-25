# Changelog — polymath-flows

## [Unreleased]

### Added

- mustPass v0.2 contract — `artifactSchemaStrict`, `diffConstraint`, and per-check `severity` (advisory / blocking). `stepSummaryMatches` is now advisory by default. `polymath-flow validate` warns when a workflow lacks any strong-deterministic blocking gate. `shipFeature.yaml` migrated to the new gates; the hollow-run falsifiability anchor (unit test + CI job) proves the gates are load-bearing. See the root `CHANGELOG.md` for the full description.
- Initial v0.1 components: `run-workflow`, `resume-workflow`, `list-workflows` skills.
- `bin/polymath-flow` deterministic executable (validate, start, next, complete, fail, resume, assert, list).
- `workflows/shipFeature.yaml` — PRD → acceptance → implement → review → verify → changelog → PR draft.
- Embedded minimal YAML subset parser fallback when PyYAML is unavailable.
- `topology: fanout` accepted on workflow steps; `artifactValid` mustPass check (PRD, ADR, Postmortem, ThreatModel).
- `workflows/reviewPR.yaml` — orient (series) then four parallel critics declared with `topology: fanout` (correctness, coverage, security, challenge), reduced by a synthesize step. Depends on polymath-engineering, polymath-qa, polymath-security, polymath-thinking.
- `workflows/respondToIncident.yaml` — page-context → triage → query-during-incident → postmortem → file-bugs. Depends on polymath-incident, polymath-connector-pagerduty, polymath-connector-datadog, polymath-connector-jira. mustPass includes `artifactValid` against the Postmortem schema.
- Workflow library expansion wave 1:
  - `workflows/bugTriage.yaml` — 5-whys → read-code → code-review → work-breakdown. Depends on polymath-thinking, polymath-engineering, polymath-planning.
  - `workflows/perfRegression.yaml` — datadog signals → code-review → feature-dev → verify-change. Depends on polymath-connector-datadog, polymath-engineering.
  - `workflows/refactorWithSafety.yaml` — read-code → coverage-gap → unit-tests (pin current behavior) → feature-dev → verify-change → code-review. Depends on polymath-engineering, polymath-qa.
  - `workflows/securityFinding.yaml` — owasp-review → stride-threat-model → feature-dev → code-review → verify-change. Depends on polymath-security, polymath-engineering.
- Schema fix: workflow `invoke` regex now allows skill names starting with a digit (e.g. `polymath-thinking:5-whys`). Was rejecting `5-whys` as invalid.
- Workflow library expansion wave 2:
  - `workflows/bumpDependency.yaml` — snyk triage → read-code → smallest bump → review → verify. Depends on polymath-connector-snyk, polymath-engineering. mustPass guards against scope creep (review-checks-scope regex).
  - `workflows/migrateLanguageVersion.yaml` — TypeScript migration in phases (plan → PIN → FIX → STRICT → review). Depends on polymath-lang-typescript, polymath-engineering. mustPass requires the plan to categorize breaking changes (`(breaking\|strictness\|inference\|removal)` regex).
  - `workflows/sunsetCapability.yaml` — write-sunset-notice → deprecate-in-code → remove-if-stage-allows → verify → release-notes. Two-stage (announce / remove). Depends on polymath-content, polymath-engineering, polymath-release. mustPass enforces sunset-notice contains both dates + replacement.
  - `workflows/featureFromIdea.yaml` — extends shipFeature with research: interview-guide → persona-refresh → prd → acceptance → implement → review → verify → changelog → PR. Refuses to write a PRD if interviews haven't actually run. Depends on polymath-research + the shipFeature dependency stack.
- Workflow library expansion wave 3:
  - `workflows/experimentToGA.yaml` — plan (polymath-data:run-experiment, pre-registered) → rollout-plan (polymath-connector-launchdarkly:flag-rollout-plan) → launch-checklist → results-analysis (against frozen plan) → GA decision artifact. mustPass enforces primary+guardrails, stop conditions, and that results reference pre-registration.
- Workflow library expansion wave 4:
  - `workflows/weeklyReleaseTrain.yaml` — collect (Conventional-Commits grouped diff since last tag) → changelog-audit → release-notes → verify → internal-heads-up → tag-pr (dryRun gate). mustPass: survey + release-notes + headline + internal advisory + verify-tests + tag artifact.
  - `workflows/incidentRetroToActions.yaml` — read-postmortem → classify (prevent/detect/mitigate/process; rewrite blame-shaped) → work-breakdown (PR-sized leaves) → estimate (XS-L; flag oversize) → file-tickets (back-linked to postmortem) → backlink (postmortem updated with ticket keys) → review. mustPass enforces artifacts at each stage, category coverage, ticket-key regex, review confirms tracking.
  - `workflows/deprecationToRemoval.yaml` — multi-quarter: stage=announce writes notice + baseline usage + adds deprecation warnings; stage=midterm measures usage decline vs baseline + emits `midterm-gate: PASS/FAIL`; stage=remove performs the removal only when removalDate has arrived AND midterm-gate PASSed. mustPass enforces dates + replacement + usage-section + midterm-gate emission + verify-tests.
