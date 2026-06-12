# Changelog — polymath-flows

## [Unreleased]

### Added

- **Opt-in run provenance.** `provenance.runs: true` in
  `.polymath/project.yaml` makes the runner whole-copy each COMPLETED run
  record (state, inputs, trace, step summaries, artifacts) into
  `.polymath/runs/<run_id>/` — versionable with the repo. Whole-copy,
  never sliced; fail-open (a copy failure never fails the run); the
  assert output reports the destination as `provenance`.
- **Opt-in local-only telemetry.** With exactly `POLYMATH_TELEMETRY=1`,
  every runner invocation appends command + workflow name + duration +
  exit code to `telemetry.jsonl` in the plugin data dir. No run ids, no
  content, no network — the complete payload is documented in
  `docs/TELEMETRY.md` (since merged into `docs/PRIVACY.md`); unset or
  any other value writes nothing (unit-gated).
- **Build-time `extends` flattening.** `polymath-flow flatten
  <partial.yaml> [--out <file>] [--check]` composes a partial (extends +
  override/insertAfter/steps/mustPass/guards) with its catalog parent
  into a standalone workflow, stamps a `provenance` block (extends ref,
  parent version, sha256 over both sources), and `--check` is a drift
  lint that exits 1 when the flattened file is stale. The runner now
  **hard-errors** on `extends`/`override`/`insertAfter` at
  validate/start and on the next/assert reload path — runtime merging
  never happens. The workflow schema gained the missing top-level
  if/then: partials validate without name/version/steps; extends-free
  workflows keep the full contract.
- **`appStarts` gate type.** Boot-verifies the app from the frozen
  project snapshot's `smoke.<lang>` recipe (HTTP path, boot-log pattern,
  or TCP-port readiness within `timeout_seconds`; `credentials_file`
  values are injected, never logged). Counts as a strong gate. Resolves
  a third, non-blocking outcome — `not-applicable`, reported in the
  result's `not_applicable` array — when the repo declares no matching
  recipe or the credentials file is absent on this machine.
- **`connectorAvailable` gate type.** Pass iff the named capability has
  a provider configured in `.polymath/capabilities.yaml` and an adapter
  plugin resolves; optional `provider` pin. Built for `guards:`.
- **Guards now execute.** `guards:` run at `start` after validation and
  capability resolution, before any run state is created: a blocking
  guard failure prints `{"status": "guard-failed", …}` and exits 2
  without littering the run store; advisory failures and not-applicable
  outcomes are reported on the start payload.
- **Project workflows are discoverable.** The SessionStart hook indexes
  project-layer (`./.claude/polymath/workflows/`) and user-layer
  workflows into a machine-local tiered fragment
  (`${CLAUDE_PLUGIN_DATA}/polymath-flows/workflow-index.project.json`)
  and appends a "Project workflows" block to the injected catalog index.
  Entries are keyed by **file stem** — the handle `start` resolves — with
  a diverging YAML `name:` recorded as `declaredName` (and `flatten
  --out` warns on the mismatch). Project tier shadows user tier;
  catalog-name shadowing is annotated; trigger phrases colliding with
  catalog triggers (or an earlier tier) are dropped and recorded in the
  fragment — never an error. A workflow needs a one-line `whenToUse` to
  be indexed; repos with no project/user workflows keep a byte-identical
  injection.

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

### Fixed

- `incidentRetroToActions`'s `postmortem-readable` guard referenced
  `${POLYMATH_INPUT_POSTMORTEMPATH}`, a convention nothing sets — inert
  while guards were unexecuted, but a permanent start-refusal once they
  run. It now uses `${inputs.postmortemPath}` like the rest of the
  workflow.
- `stepSummaryMatches` is rejected in `guards:` (schema + runner): no
  step summaries exist before any step has run, so it could never pass.

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
