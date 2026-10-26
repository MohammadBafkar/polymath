---
name: run-workflow
description: Run a flows-lite workflow end-to-end; the skill drives the loop while bin/polymath-flow owns YAML validation, state, and mustPass checks.
---

# run-workflow

> Drive a flows-lite workflow from start to completion. This skill is the human-facing presenter; the deterministic state machine is the bundled `bin/polymath-flow` runner.

## When to use

- The user types `/polymath-flows:run-workflow <name> ...`.
- A user types something like "ship a small feature for X" and `shipFeature` is the appropriate workflow.

## Detect → propose → confirm → run

The SessionStart hook injects a compact `name: whenToUse` index of every workflow
(built into `data/workflow-index.min.json`), so you can recognise when a request
matches a multi-step arc instead of waiting to be told the workflow's name. A
workflow is a state machine the user opts into — **never auto-start one**, headless
or interactive. (`trust: auto-headless` in a surface's routing lets a read-only,
non-workflow surface skip the propose step in a non-interactive session; it never
applies to workflows.) Follow this contract:

1. **Detect.** Compare the request to the injected `whenToUse` lines. To break ties
   between colliding workflows you MAY read `data/workflow-detect.json` and weigh
   its `paths`/`intents` signals (e.g. a `docs/plans/**` path raises `reviewPlan`).
   Pick at most one primary candidate (plus an optional runner-up).
2. **Propose (one line, no work yet).** e.g. *"This looks like the `reviewPlan`
   workflow (critique an existing plan, findings only). Run it? (yes / just answer
   directly / a different workflow)"*. If two candidates tie, name the alternative
   in the same sentence.
3. **Await approval.** Do NOT call `bin/polymath-flow` until the user agrees. On
   "just answer"/"no", drop the workflow, answer directly with plain skills, and do
   not re-propose the same workflow this turn.
4. **Run.** On approval, proceed with the Procedure below.

Guardrails: propose at most once per turn; never propose a workflow whose
`requires` plugins/capabilities are unmet (surface the missing dependency
instead); if the user names a workflow explicitly ("run shipFeature"), skip the
proposal and run it; for `respondToIncident`-style sev1/sev2 phrasings, still ask
in one line unless the user said "just do it".

## Inputs

- Workflow name (required): e.g. `shipFeature`.
- Inputs in the form `key=value` (e.g. `title="Rate-limit /login"`, `scope=small`).

## Procedure

The runner ships in this plugin's `bin/` (also on the shell `PATH` while the plugin is enabled). Each command below spells out the full path because shell variables don't survive between separate tool calls.

1. **Start the run.** Execute:

   ```bash
   "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" start <name> --input key=value [--input key=value ...]
   ```

   Parse the returned `run_id`. If the executable reports validation errors or unmet guards, surface them verbatim and stop.

2. **Loop until the workflow completes or pauses.** For each iteration:

   a. Ask the executable for the next step:

      ```bash
      "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" next <run_id>
      ```

      The output JSON contains `step_id`, `invoke` (routing label), `prompt`, and any expected `artifacts`.

   b. Announce the step to the user with one sentence: "Step <n> of <total>: <step_id> — <prompt>".

   c. **Perform the work for this step in the current turn.** `invoke` is a routing label (`polymath-product:prd`), not a programmatic call: load that skill (via your skill tool, or read its `SKILL.md`) and follow its procedure with the step `prompt` and inputs as its input. If the named skill is not installed, say so and `fail` the step rather than improvising its procedure.

   d. Write any declared `artifacts` to disk, then check each one exists and is non-empty before completing the step.

   e. Compose a one-paragraph **step summary** of what actually happened — files changed, commands run, and their real results — save it to a file (`mktemp`), and tell the executable:

      ```bash
      "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" complete <run_id> <step_id> --summary <summary-file>
      ```

      Some workflows gate on the summary text (`stepSummaryMatches`, e.g. a verify step expecting "tests"/"verified"). Those gates only mean something if the summary is honest: report the verification you actually ran and its outcome. If verification did not run or failed, say so and `fail` the step — never add the gate's words to get past it.

   f. If a step fails or the user wants to pause, record the reason (inline text, not a file):

      ```bash
      "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" fail <run_id> <step_id> --summary "<one-line reason>"
      ```

      Then stop the loop and report.

3. **Assert.** After all steps are complete, run:

   ```bash
   "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/polymath-flow" assert <run_id>
   ```

   This evaluates all `mustPass` checks. If any fail, the workflow is paused; report the failures and stop. The user can resume with `/polymath-flows:resume-workflow <run_id>` after addressing them.

4. **Offer the next arc.** On `completed`, if the output JSON includes `chainsTo`,
   propose the named next arc(s) in one line under the same detect → propose →
   confirm contract (**never auto-start**), e.g. *"Incident closed. The natural
   next arc is `incidentRetroToActions` (turn the postmortem into filed actions).
   Run it? (yes / not now)"*.

## Reporting

- One line per step: status + key artifact.
- Final line: `completed` or `paused` with `mustPass` failure summary.
- If a workflow is paused, surface the resume command.

## Anti-patterns to avoid

- Skipping the executable and managing state internally (defeats determinism and resumability).
- Treating `invoke` as a slash-command call. It is a label.
- Marking a step `complete` without writing the declared artifacts.
- Padding a step summary with the words a `stepSummaryMatches` gate looks for when the work behind them did not happen.
- Editing files outside the declared `artifacts` for a step unless the workflow step's `prompt` explicitly authorizes it.
