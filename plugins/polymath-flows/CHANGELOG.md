# Changelog — polymath-flows

## [Unreleased]

### Added

- Workflow discoverability: every workflow now declares optional
  `whenToUse` / `triggers` / `detectionSignals`, and a SessionStart hook
  injects a compact routing index (built by `tools/build-workflow-index.py`
  into `data/`) so the agent can detect and propose a matching workflow
  before running it. The `run-workflow` skill documents the
  detect → propose → confirm → run contract; a `WORKFLOW-INDEX` conformance
  diff-guard keeps the committed index in sync with the workflow YAML.
- `reviewPlan` workflow: lightweight multi-critic critique of an existing
  plan/design doc (red-team + pre-mortem + tradeoffs → synthesis), findings
  only — no revised plan, no governance.
- `activateProject` workflow to generate `.polymath/project.yaml`,
  capability mappings, and onboarding notes for a repository.
- `deliberationLoop` workflow to observe, frame, compare options,
  red-team the recommendation, and write a revised plan.

## [0.1.0]

### Added

- `run-workflow`, `resume-workflow`, `list-workflows` skills.
- `bin/polymath-flow` deterministic executable (`validate`, `start`,
  `next`, `complete`, `fail`, `resume`, `assert`, `list`,
  `calibrate`).
- Minimal YAML subset parser fallback when PyYAML is unavailable.
- `mustPass` types: `fileExists`, `fileMatches`, `commandSucceeds`,
  `stepSummaryMatches`, `command`, `artifactValid`,
  `artifactSchemaStrict`, `diffConstraint`, each with optional
  `severity: advisory | blocking`.
- `topology: fanout` accepted on steps (executor runs serially today
  but surfaces the intent).
- Capability layer: workflows declare `requires.capabilities` and the
  runner resolves the provider from `.polymath/capabilities.yaml`,
  expanding `${capabilities.<cap>.provider}` /
  `${capabilities.<cap>.plugin}` placeholders.
- 15 workflows under `workflows/`:
  - `shipFeature` — PRD → acceptance → implement → review → verify
    → changelog → PR draft.
  - `reviewPR` — orient (series) then four parallel critics
    (correctness, coverage, security, challenge) declared as
    `topology: fanout`, reduced by a synthesize step.
  - `respondToIncident` — page-context → triage →
    query-during-incident → postmortem → file-bugs. Capability-shaped
    (`pager`, `observability`, `issue_tracker`).
  - `bugTriage` — 5-whys → read-code → code-review → work-breakdown.
  - `perfRegression` — observability signals → code-review →
    feature-dev → verify-change. Capability-shaped (`observability`).
  - `refactorWithSafety` — read-code → coverage-gap → unit-tests
    (pin current behavior) → feature-dev → verify-change →
    code-review.
  - `securityFinding` — owasp-review → stride-threat-model →
    feature-dev → code-review → verify-change.
  - `bumpDependency` — vuln triage → read-code → smallest bump →
    review → verify. Capability-shaped (`vulnerability_scanner`).
  - `migrateLanguageVersion` — language-agnostic migration plan →
    apply → verify. Detects the project's language at runtime.
  - `sunsetCapability` — write-sunset-notice → deprecate-in-code →
    remove-if-stage-allows → verify → release-notes.
  - `featureFromIdea` — extends `shipFeature` with interview-guide →
    persona-refresh upstream.
  - `experimentToGA` — plan → rollout → launch-checklist →
    results-analysis (against frozen plan) → GA decision artifact.
  - `weeklyReleaseTrain` — collect → changelog-audit → release-notes
    → verify → internal-heads-up → tag-pr (dryRun gate).
  - `incidentRetroToActions` — read-postmortem → classify (prevent /
    detect / mitigate / process) → work-breakdown → estimate →
    file-tickets → backlink → review. Capability-shaped
    (`issue_tracker`).
  - `deprecationToRemoval` — multi-stage: announce (write notice +
    deprecation warnings + baseline usage), midterm (measure usage
    decline; emit `midterm-gate: PASS/FAIL`), remove (only when
    `removalDate` arrived AND `midterm-gate` PASSed).
