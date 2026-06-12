# Changelog — polymath-pipeline

## [Unreleased]

### Added

- **Enforce-gate hole closure.** The PreToolUse matcher now also covers
  `Task` and `mcp__.*`. MCP tools default to gated unless their name
  classifies as read-only (first verb segment wins; `get_file_contents`
  passes, `push_files` and unknown names are gated). `Task` requires a
  fresh classification. The Bash modify-pattern blacklist gains nine
  patterns covering the eleven sampled mutators it previously missed
  (`make`, interpreter-runs-script, `npx`, `gh`/`az`/`gcloud`/`aws`
  mutating subcommands, database CLIs, `rsync`/`scp`/`sftp`/`unzip`,
  command-position `patch`, `tar` create/extract) — each pinned by a
  fixture, with command-position anchors keeping argument words exempt
  and a deadlock-guard test pinning that the `mark` recovery command
  itself always passes.
- **Data-driven tool policy.** Base policy ships in
  `data/tool-policy.json` (mirrored by engine constants as the
  fail-safe; a unit test pins the two equal). Projects can strengthen it
  via `.polymath/tool-policy.json` (`gatedTools`, `bashModifyPatterns`,
  `mcpGatedPatterns`, `mcpMutatingVerbs`); weakening keys are ignored
  and audited (`policy-overlay-ignored`, `policy-overlay-invalid`,
  `policy-bad-pattern` decision events).
- **Feedback loop (capture → evaluate → apply).**
  `polymath-pipeline feedback capture|digest|evaluate|resolve`: an
  event-sourced JSONL store with a 180-day TTL (digest sweeps expired
  items). `feedback-capture` skill: conservative criteria — named
  surface, user-confirmed, localization fix conceivable, never secrets.
  `feedback-digest` skill: every item gets a verdict with evidence
  (valid-constructive / valid-not-actionable / invalid); project-local
  fixes (conventions docs, `skill_overrides`,
  `route-signals.project.json`) are applied behind ONE confirmation;
  catalog-level findings are emitted only as proposed patch files under
  `.polymath/feedback/catalog-proposals/` — never auto-committed.
- Initial plugin (Phase 3 of `docs/plans/generalized-localization.md`,
  plan file since removed).
  Opt-in on `routing.mode: classify|enforce`:
  - `bin/polymath-pipeline` engine: shared root resolver (refusing `$HOME`
    and `${CLAUDE_CONFIG_DIR}`), overlay-aware `routing.mode` line-scan,
    per-invocation session-namespaced markers, append-only decision log
    with retention sweep, `mode`/`mark`/`status`/`sweep` CLI.
  - Classify directive (UserPromptSubmit): emitted while the session has no
    fresh classification; route-hint precedence; honors
    `trust: auto-headless` for read-only surfaces (first consumer of the
    declared trust axis); audited kill switch
    (`POLYMATH_PIPELINE_OFF=1` / `.polymath/pipeline-off`).
  - Enforce gate (PreToolUse): blocks mutating tool calls (modify-pattern
    Bash blacklist with accepted false positives; Edit/Write always gated)
    until `mark` recorded a classification (1 h validity); every deny,
    kill-switch use, and fail-open is audited.
  - `intake` skill: 4 confidence dimensions, batched questions, plateau
    stop, never-ask list, smallest-surface routing, ends with `mark`.
