# Changelog — polymath-pipeline

## [Unreleased]

### Added

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
