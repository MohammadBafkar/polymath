---
name: run-workflow
description: Run a flows-lite workflow end-to-end; the skill drives the loop while bin/polymath-flow owns YAML validation, state, and mustPass checks.
---

# run-workflow

> Drive a flows-lite workflow from start to completion. This skill is the human-facing presenter; the deterministic state machine lives in `${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow`.

## When to use

- The user types `/polymath-flows:run-workflow <name> ...`.
- A user types something like "ship a small feature for X" and `shipFeature` is the appropriate workflow.

## Detect → propose → confirm → run

The SessionStart hook injects a compact `name: whenToUse` index of every workflow
(built into `data/workflow-index.min.json`), so you can recognise when a request
matches a multi-step arc instead of waiting to be told the workflow's name. A
workflow is a state machine the user opts into — **never auto-start one.** Follow
this contract:

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

1. **Start the run.** Execute:

   ```bash
   ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow start <name> --input key=value [--input key=value ...]
   ```

   Parse the returned `run_id`. If the executable reports validation errors, surface them and stop.

2. **Loop until the workflow completes or pauses.** For each iteration:

   a. Ask the executable for the next step:

      ```bash
      ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow next <run_id>
      ```

      The output JSON contains `step_id`, `invoke` (routing label), `prompt`, and any expected `artifacts`.

   b. Announce the step to the user with one sentence: "Step <n> of <total>: <step_id> — <prompt>".

   c. **Perform the work for this step in the current turn**, guided by the `invoke` capability label. For v0.1, `invoke` is a routing label, not a programmatic slash-command call: treat it as guidance about which skill's procedure to follow (e.g. `polymath-product:prd` → use the `prd` skill from `polymath-product`).

   d. Write any declared `artifacts` to disk.

   e. Compose a one-paragraph **step summary** describing what changed and pointing to files. Save to a temporary file and tell the executable:

      ```bash
      ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow complete <run_id> <step_id> --summary <summary-file>
      ```

      The summary must include the words "test", "tests", "verified", or "verification" for the `verify` step so the `shipFeature` workflow's `stepSummaryMatches` check passes.

   f. If a step fails or the user wants to pause, run:

      ```bash
      ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow fail <run_id> <step_id> --summary <reason>
      ```

      Then stop the loop and report.

3. **Assert.** After all steps are complete, run:

   ```bash
   ${CLAUDE_PLUGIN_ROOT}/bin/polymath-flow assert <run_id>
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
- Editing files outside the declared `artifacts` for a step unless the workflow step's `prompt` explicitly authorizes it.
