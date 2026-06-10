# Changelog — polymath-flows

## [Unreleased]

### Added

- **`${project.*}` placeholders.** Step `prompt`/`artifacts` and mustPass
  `path`/`command` can reference the project-context snapshot
  (`${project.stack.languages.0.lang}`); numeric segments index lists,
  mappings render as compact JSON. The snapshot is frozen into
  `state.json` at `start` (like the capability map), resolved from
  polymath-core's data dir including the per-plugin+marketplace
  namespaced layout, newest mtime wins, degrade-quiet when absent.
  `${project.<path>:-fallback}` uses the fallback on a miss or when no
  snapshot exists — the only form safe in marketplace workflows;
  `polymath-flow validate` warns on the bare form.
- Four composed workflow arcs: `prdToShip` (ship from an existing PRD),
  `estimateAndPlan` (clear goal → WBS + estimate + plan), `requirementsToBacklog`
  (PRD → decomposed/groomed/estimated backlog), and `progressiveRollout` (staged
  flag rollout with SLO gates, no A/B). Each ships routing metadata + a
  workflow-triggering test. The injected index token ceiling was recalibrated
  (450 → 560) for the workflow set — the last flat-surface bump before a tiered
  injection at ~30.
  - A fifth arc, `incidentToReview`, was dropped before release: it competed
    head-to-head with the `respondToIncident → incidentRetroToActions` chain on
    the same `docs/postmortems/**` detect path. Its arc trigger phrasings were
    migrated onto `respondToIncident` (which `chainsTo incidentRetroToActions`).

- Workflow discoverability: every workflow now declares optional
  `whenToUse` / `triggers` / `detectionSignals`, and a SessionStart hook
  injects a compact routing index (built by `tools/build-workflow-index.py`
  into `data/`) so the agent can detect and propose a matching workflow
  before running it. The `run-workflow` skill documents the
  detect → propose → confirm → run contract; a `WORKFLOW-INDEX` conformance
  diff-guard keeps the committed index in sync with the workflow YAML. The
  `WORKFLOW-2` gate (`build-workflow-index.py --strict`) requires `whenToUse`
  and `triggers` on every workflow and rejects triggers shared across workflows.
- Workflow-triggering tests (`tools/workflow-triggering.py`,
  `tests/workflow-triggering/*.md`): a naive prompt must make the model propose
  the right workflow. `check` mode (frontmatter + trigger-drift guard) runs in
  conformance; `run` mode is opt-in under `CLAUDE_CODE_OAUTH_TOKEN`.
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
