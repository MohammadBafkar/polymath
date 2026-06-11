# polymath-flows

flows-lite: a deterministic serial workflow runner for the Polymath marketplace. v0.1 ships SDLC workflows such as `shipFeature`, `activateProject`, and `deliberationLoop`.

## What it ships

- Skills: `run-workflow`, `resume-workflow`, `list-workflows`.
- Executable: `bin/polymath-flow` — owns YAML validation, guard preconditions, state, mustPass checks (including the `appStarts` boot-verification and `connectorAvailable` presence gates), and build-time `extends` flattening (`flatten` / `flatten --check` drift lint; the runner hard-errors on runtime `extends`); opt-in run provenance (`provenance.runs: true` whole-copies completed run records to `.polymath/runs/`); and opt-in local-only telemetry (`POLYMATH_TELEMETRY=1`, see `docs/TELEMETRY.md`).
- Workflows: YAML files under `workflows/`, including `activateProject`, `deliberationLoop`, `shipFeature`, `reviewPlan`, and the thinking/design family `decideUnderAmbiguity`, `rootCauseAnalysis`, `fuzzyGoalToPlan`, and `designSystem`.
- Routing surface: a SessionStart hook (`hooks/`) injects a compact `name: whenToUse` index of every workflow so the agent can **detect** a matching arc and **propose** it before running, instead of only running one by name. The catalog index is built by `tools/build-workflow-index.py` into `data/` (the single producer; a conformance diff-guard keeps it from drifting); the hook additionally indexes project-layer (`./.claude/polymath/workflows/`) and user-layer workflows into a machine-local fragment (`${CLAUDE_PLUGIN_DATA}/polymath-flows/workflow-index.project.json`, trigger collisions with the catalog dropped) and appends them as a "Project workflows" block. Each workflow declares `whenToUse` / `triggers` / `detectionSignals`; mute the surface with `touch "$CLAUDE_PLUGIN_DATA/polymath-flows/index-muted"`.

## Why two layers (skill + executable)?

Claude Code's runtime is a single LLM-driven loop. It has no built-in DAG executor, state store, resumable runner, or nested slash-command invoker. So:

- The **skill** drives the loop, announces steps, and performs the actual Claude work (PRD drafting, implementation, review, …).
- The **executable** owns deterministic concerns: validating YAML, advancing state, evaluating `mustPass`.

Neither alone is sufficient. Both must work for v0.1 to pass.

## State

Run state lives under `${CLAUDE_PLUGIN_DATA}/workflows/<run_id>/`:

```text
state.json        — current step index, status, per-step status
inputs.json       — user-supplied inputs
trace.jsonl       — append-only event log
budget.json       — runtime token estimate (soft/hard ceiling)
step-summaries/<step-id>.md
artifacts/        — files the workflow produced (optional)
```

## Installation

```bash
claude plugin install polymath-flows@polymath
```

## Dependencies

- `polymath-core`
- `polymath-product`
- `polymath-engineering`
- `polymath-release`

## Running the golden demo

```bash
claude
> /polymath-flows:run-workflow activateProject
> /polymath-flows:run-workflow deliberationLoop subject="Project onboarding for Polymath" mode=plan
> /polymath-flows:run-workflow shipFeature title="Rate-limit /login" scope=small
```

The session must produce a PRD, acceptance criteria, an implementation diff, a code-review summary, a CHANGELOG entry, and a PR draft. Resumption is verified with `/polymath-flows:resume-workflow`.

## Out of scope (v0.1)

- Parallel steps.
- Agent panels.
- Connector events (`wait-for-event`).
- AI-based cross-artifact alignment as a blocking gate.
- Real PR creation through GitHub.

## License

MIT.
