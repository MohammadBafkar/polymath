# polymath-pipeline

Opt-in routing pipeline. A repo that declares `routing.mode: classify` or
`enforce` in `.polymath/project.yaml` gets an explicit classify-before-work
loop — a per-prompt classify directive, an intake skill for ambiguous
requests, and (in `enforce`) a gate that blocks mutating tool calls until
the request has been classified. A repo without that declaration pays three
constant-time early-exits per session and nothing else; `hint` mode stays
exactly polymath-core's ambient route-hint behavior.

## What it ships

- Skills: `intake` — classify an ambiguous or multi-step request: score 4
  confidence dimensions (intent, scope, constraints, acceptance), ask only
  what the repo can't answer (never-ask list), stop at plateau, record the
  route.
- Executable: `bin/polymath-pipeline` — the engine: shared project-root
  resolver (refuses `$HOME` and `${CLAUDE_CONFIG_DIR}` as roots),
  `routing.mode` reader (overlay-aware line-scan, no PyYAML dependency),
  session-namespaced markers, append-only decision log + retention sweep,
  and the `mode` / `mark` / `status` / `sweep` CLI.
- Hooks:
  - `SessionStart` — announces the active mode for the repo and runs the
    retention sweep (markers > 7 days pruned; decision log truncated to its
    newest 1000 lines past 512 KiB). Silent for unconfigured repos.
  - `UserPromptSubmit` — emits the classify directive while the session has
    no fresh classification (1 hour validity), and stamps the
    per-invocation session marker. The directive encodes route-hint
    precedence (a `[polymath-core route]` hint wins) and honors
    `trust: auto-headless` for read-only surfaces — the first consumer of
    the declared trust axis.
  - `PreToolUse` (`Bash|Edit|Write|MultiEdit|NotebookEdit`) — the enforce
    gate, active only when `routing.mode: enforce`: read-only Bash is
    exempt via a modify-pattern blacklist (false positives accepted — they
    cost one classify round-trip), everything mutating needs a fresh
    classification; deny = exit 2 with the recovery instruction.

## The loop

1. Prompt arrives → the directive asks the model to classify: follow the
   route hint if one fired, run `intake` for ambiguous/multi-step asks, or
   just answer a trivial turn.
2. The model records the choice:
   `bin/polymath-pipeline mark --surface <skill|workflow|direct>` (1 h
   validity, root-scoped).
3. In `enforce` mode, mutating tool calls are blocked until step 2
   happened; read-only investigation is never blocked.

## Escape hatches (audited)

`POLYMATH_PIPELINE_OFF=1` or `touch .polymath/pipeline-off` switches the
pipeline off; every use is appended to the decision log
(`${CLAUDE_PLUGIN_DATA}/decisions.jsonl`), as is every enforce denial and
every internal fail-open. The pipeline never breaks a turn: any error in a
hook fails open and is logged.

## State

```text
${CLAUDE_PLUGIN_DATA}/
  markers/<session>.json   # per-invocation stamps + classified_at
  decisions.jsonl          # audit: classify-directive, classified,
                           # enforce-deny, kill-switch, fail-open, sweep
```

## Limitations

- The `routing.mode` reader is a line-scan for the block form
  (`routing:` newline `  mode: …`); a flow-style `routing: {mode: …}`
  reads as `hint`.
- `mark` runs through the Bash tool, which cannot know the harness session
  id — markers are stored session-namespaced but accepted root-scoped
  within the 1 h TTL.

## Installation

```bash
claude plugin install polymath-pipeline@polymath
```
