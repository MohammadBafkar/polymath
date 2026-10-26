---
name: doctor
description: Check the Polymath environment — required and optional tools, and validate any .polymath/project.yaml — reporting PASS/WARN/FAIL and fix hints.
---

# doctor

> A fast environment preflight. Run it first when Polymath behaves oddly, or as
> step 0 of project initialization, so missing tools surface as actionable
> guidance instead of a cryptic shell error.

**Mode:** deterministic — same inputs, same output. Follow the steps and the output shape exactly; compute with the named script or tool, never by estimate; add nothing the shape does not ask for.

## When to use

- A new contributor just installed Polymath and wants to confirm their machine is ready.
- The SessionStart hook printed nothing, or a workflow failed with a tool error.
- `initialize-project` calls this as step 0 before it does any inference.

## Inputs

- None required. Run from the repository root so the project-file and routing checks see this repo.

## Procedure

1. Run the bundled checker from the repo root:
   ```bash
   bash "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/doctor/scripts/doctor.sh"
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

The script's report verbatim, then one fix line per `✗` / `!`:

```text
polymath-core:doctor — environment preflight

Required:
  ✓ bash       GNU bash, version 5.2.21(1)-release
  ✓ python3    Python 3.12.3

Recommended:
  ✓ git        git version 2.43.0
  ! claude     not found — install Claude Code to run plugin validation and fixtures

Optional:
  ✓ PyYAML     present (richer project.yaml parsing)
  ! jq         not found (optional)

Project context:
  ! no .polymath/project.yaml — run /polymath-core:init-project

Routing pipeline:
  ✓ routing    mode=hint — ambient route hints only

doctor: OK — required tools present.

Fixes: install the claude CLI (recommended) · run /polymath-core:init-project
```

## Quality bar

- Never reports a tool as required unless Polymath actually needs it (`jq` is
  optional; PyYAML is optional because the loader has a fallback).
- Reports project-file validity using the real loader, not a re-implementation.
- Exits non-zero on a missing required tool so it can gate `initialize-project`.
