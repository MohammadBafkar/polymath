---
name: resume-workflow
description: Resume a paused flows-lite workflow run from the last completed step using bin/polymath-flow resume.
---

# resume-workflow

> Resume a paused workflow. Pause causes include user interrupt, step failure, or a failed `mustPass` check.

**Mode:** deterministic — same inputs, same output. Follow the steps and the output shape exactly; compute with the named script or tool, never by estimate; add nothing the shape does not ask for.

## When to use

- The user types `/polymath-flows:resume-workflow [<run_id>]`.
- The `polymath-core` SessionStart hook surfaced a paused OR an in-progress
  (active) run — including one interrupted in a prior session, possibly flagged stale.
- A `mustPass` failure paused a previous run.

## Inputs

- Optional `run_id`. If omitted, list paused and in-progress runs and ask which to resume.

## Procedure

1. If no `run_id` was supplied, list both resumable buckets:

   ```bash
   "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" list --status paused
   "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" list --status active
   ```

   Surface the combined table (`run_id` + status + `last_active`) and ask the user to
   pick one. If both are empty, say so and stop. `resume` continues an active run
   as-is and flips a paused run back to active.

2. Resume the chosen run:

   ```bash
   "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" resume <run_id>
   ```

   The executable flips status from `paused` to `active` and prints the next step JSON.

3. Continue the loop exactly as `run-workflow` does: announce step → perform work → write artifacts → `complete` → `assert` at the end.

## Output

```text
Resuming 2026-10-21T09-10-shipFeature-resilient-retries  (paused: mustPass pr-draft-exists failed)
Fixed first: wrote docs/pr/resilient-retries.md
  6/6 pr             complete   docs/pr/resilient-retries.md
assert: completed — 4/4 mustPass checks passed
```

Then the same per-step lines as `run-workflow`. With no `run_id` and nothing
resumable: `No paused or active runs.`

## Anti-patterns to avoid

- Resuming without checking *why* it paused. If a `mustPass` check failed, the underlying artifact must actually be fixed (e.g. the missing PRD written) before resuming — never by editing a step summary to match the gate.
- Resuming a run flagged stale (≥ 2 days idle) without first checking that the branch, artifacts, and inputs it depends on still exist.
- Re-doing already-complete steps. The executable's `next` always points to the right place; trust it.
