# polymath-flows

flows-lite: a deterministic serial workflow runner for the Polymath marketplace. v0.1 ships the `shipFeature` workflow end-to-end.

## What it ships

- Skills: `run-workflow`, `resume-workflow`, `list-workflows`.
- Executable: `bin/polymath-flow` — owns YAML validation, state, mustPass checks.
- Workflows: `workflows/shipFeature.yaml`.

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

Apache-2.0.
