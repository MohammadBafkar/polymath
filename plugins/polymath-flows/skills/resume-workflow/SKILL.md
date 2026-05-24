---
name: resume-workflow
description: Resume a paused flows-lite workflow run from the last completed step using bin/polymath-flow resume.
---

# resume-workflow

> Resume a paused workflow. Pause causes include user interrupt, step failure, or a failed `mustPass` check.

## When to use

- The user types `/polymath-flows:resume-workflow [<run_id>]`.
- The `polymath-core` SessionStart hook surfaced one or more paused workflows.
- A `mustPass` failure paused a previous run.

## Inputs

- Optional `run_id`. If omitted, list paused runs and ask the user which to resume.

## Procedure

1. If no `run_id` was supplied, run:

   ```bash
   ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow list --status paused
   ```

   Surface the table and ask the user to pick one. If none are paused, say so and stop.

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
