# polymath-pipeline

Opt-in routing pipeline. A repo that declares `routing.mode: classify` or
`enforce` in `.polymath/project.yaml` gets an explicit classify-before-work
loop — a per-prompt classify directive, an intake skill for ambiguous
requests, and (in `enforce`) a gate that blocks mutating tool calls until
the request has been classified. A repo without that declaration pays three
constant-time early-exits per session and nothing else; `hint` mode stays
exactly polymath-core's ambient route-hint behavior.

## What it ships

- Skills:
  - `intake` — classify an ambiguous or multi-step request: score 4
    confidence dimensions (intent, scope, constraints, acceptance), ask only
    what the repo can't answer (never-ask list), stop at plateau, record the
    route.
  - `feedback-capture` — conservatively record one localization-feedback
    item (user-confirmed correction/gap/friction tied to a named surface;
    180-day TTL; never secrets).
  - `feedback-digest` — evaluate captured items (verdict with evidence),
    apply project-local fixes behind ONE confirmation, emit catalog-level
    findings only as proposed patch files under
    `.polymath/feedback/catalog-proposals/` — never auto-committed.
- Executable: `bin/polymath-pipeline` — the engine: shared project-root
  resolver (refuses `$HOME` and `${CLAUDE_CONFIG_DIR}` as roots),
  `routing.mode` reader (overlay-aware line-scan, no PyYAML dependency),
  session-namespaced markers, append-only decision log + retention sweep,
  the `mode` / `mark` / `status` / `sweep` CLI, and the feedback store
  (`feedback capture|digest|evaluate|resolve`, event-sourced JSONL,
  180-day TTL).
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
  - `PreToolUse` (`Bash|Edit|Write|MultiEdit|NotebookEdit|Task|mcp__.*`) —
    the enforce gate, active only when `routing.mode: enforce`: read-only
    Bash is exempt via a modify-pattern blacklist (false positives
    accepted — they cost one classify round-trip); MCP tools default to
    gated unless their name classifies as read-only (first verb segment
    wins: `get_file_contents` passes, `push_files` and unknown names are
    gated); `Task` is gated; everything mutating needs a fresh
    classification; deny = exit 2 with the recovery instruction.

## Tool policy

The gate's policy — gated tools, the Bash modify-pattern blacklist, and
the MCP verb classification — ships in
[`data/tool-policy.json`](data/tool-policy.json) (mirrored by engine
constants as the fail-safe; a unit test pins the two equal). A project
can **strengthen** it with `.polymath/tool-policy.json`:

```json
{
  "gatedTools": ["WebFetch"],
  "bashModifyPatterns": ["\\bmycorptool\\b"],
  "mcpGatedPatterns": ["^mcp__internal-erp__"],
  "mcpMutatingVerbs": ["provision"]
}
```

Overlays are strengthen-only by construction: there are no keys that
exempt anything, and unknown keys (e.g. an attempted `mcpReadOnlyVerbs`)
are ignored and audited to the decision log
(`policy-overlay-ignored` / `policy-overlay-invalid`).

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
  feedback.jsonl           # event-sourced feedback store (capture /
                           # evaluate / resolve; 180d TTL)
```

## Limitations

- The `routing.mode` reader is a line-scan for the block form
  (`routing:` newline, then an indented `mode: …` line; trailing comments
  are fine). A flow-style `routing: {mode: …}` or an unknown mode value
  still reads as `hint`, but LOUDLY: SessionStart prints a
  `config error` line, `mode`/`status` report it under `config_errors`,
  and a `config-error` event is audited.
- The classify directive bakes `--session <id>` into the mark command, so
  markers are attributed to the issuing session. A mark issued without
  `--session` (headless run, hand-typed) is still accepted root-scoped
  within the 1 h TTL.
- `mark --surface` is validated against the sibling-plugin catalog
  (skills, workflow names, `direct`); when the siblings are unresolvable
  (standalone install) validation fails open.

## Installation

```bash
claude plugin install polymath-pipeline@polymath
```
