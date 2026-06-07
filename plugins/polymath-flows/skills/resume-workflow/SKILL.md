---
name: resume-workflow
description: Resume a paused flows-lite workflow run from the last completed step using bin/polymath-flow resume.
---

# resume-workflow

> Resume a paused workflow. Pause causes include user interrupt, step failure, or a failed `mustPass` check.

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
   ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow list --status paused
   ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow list --status active
   ```

   Surface the combined table (`run_id` + status + `last_active`) and ask the user to
   pick one. If both are empty, say so and stop. `resume` continues an active run
   as-is and flips a paused run back to active.

2. Resume the chosen run:

   ```bash
   ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow resume <run_id>
   ```

   The executable flips status from `paused` to `active` and prints the next step JSON.

3. Continue the loop exactly as `run-workflow` does: announce step → perform work → write artifacts → `complete` → `assert` at the end.

## Reporting

- One-line summary of why the run was paused (from `state.json`'s `pause_reason`).
- Then the same per-step reporting as `run-workflow`.

## Anti-patterns to avoid

- Resuming without checking *why* it paused. If a `mustPass` check failed, the user must fix the underlying artifact (e.g. create the missing PRD file) before resuming.
- Re-doing already-complete steps. The executable's `next` always points to the right place; trust it.
