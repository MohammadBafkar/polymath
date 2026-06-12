---
name: doctor
description: Preflight the Polymath environment — check required and optional tools and validate any .polymath/project.yaml, with PASS/WARN/FAIL and fix hints.
---

# doctor

> A fast environment preflight. Run it first when Polymath behaves oddly, or as
> step 0 of project initialization, so missing tools surface as actionable
> guidance instead of a cryptic shell error.

## When to use

- A new contributor just installed Polymath and wants to confirm their machine is ready.
- The SessionStart hook printed nothing, or a workflow failed with a tool error.
- `initialize-project` calls this as step 0 before it does any inference.

## Procedure

1. Run the bundled checker from the repo root:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/doctor/scripts/doctor.sh"
   ```
   (From inside this marketplace repo:
   `bash plugins/polymath-core/skills/doctor/scripts/doctor.sh`.)
2. Read the report. It groups results as **Required** (`bash`, `python3`),
   **Recommended** (`git`, `claude` CLI), and **Optional** (PyYAML, `jq`), then
   validates any `.polymath/project.yaml` via the SessionStart loader, and
   finally reports the **Routing pipeline**: the resolved `routing.mode`,
   any routing config errors, an engaged kill switch, and recent decision
   events for this root (enforce denials, fail-opens, kill-switch uses,
   rejected marks) — or a warning that `polymath-pipeline` is not
   installed, which would make `classify`/`enforce` declarations inert.
3. For each `✗` (required) or `!` (recommended/optional), relay the one-line fix
   hint to the user. The script exits non-zero only when a **required** tool is
   missing — that is the gate.
4. If `project.yaml` is present but the loader rejected it, show the validation
   errors and offer to re-run `polymath-core:initialize-project` to regenerate it.
5. If no `project.yaml` exists, point the user at `/polymath-core:init-project`.

## Output

- The PASS/WARN/FAIL report, plus a one-line verdict.
- For each failure, the concrete next action (install command or skill to run).

## Quality bar

- Never reports a tool as required unless Polymath actually needs it (`jq` is
  optional; PyYAML is optional because the loader has a fallback).
- Reports project-file validity using the real loader, not a re-implementation.
- Exits non-zero on a missing required tool so it can gate `initialize-project`.
