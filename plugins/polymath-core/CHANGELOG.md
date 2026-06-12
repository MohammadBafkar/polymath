# Changelog — polymath-core

## [Unreleased]

### Added

- **Opt-in hint-adoption telemetry.** With exactly
  `POLYMATH_TELEMETRY=1`, the route-hint hook appends emitted-hint
  records (surface names + timestamp, never prompt text) to
  `${CLAUDE_PLUGIN_DATA}/polymath-core/hint-log.jsonl` — local-only,
  fail-open, size-capped; the off state is unit-verified. Doctor joins
  it against polymath-pipeline `classified` events and reports how many
  recent emissions were followed by a matching mark within 30 minutes.
- **Hint render budgeted (HINT-BUDGET) + doctor shows injection
  tiering.** The route-hint trust/footer wording is tightened and the
  worst single-candidate render is gated at ≤120 tokens
  (`tools/build-surface-index.py --hint-budget`, self-tested; the
  install-affordance path is outside the budget). `doctor.sh` gains a
  *Workflow injection* section rendering polymath-flows' tiering
  record: Tier A size, repo-relevant count, Tier B pointer count, and
  any relevant-but-overflowed workflows.
- **Install-aware route hints.** When polymath-core runs from the
  install cache, the hint checks whether a matched surface's plugin is
  actually installed: an uninstalled match renders a one-line install
  affordance (`… — plugin not installed; install: claude plugin install
  <plugin>@polymath`) instead of a broken proposal, and shortlist
  candidates carry `"installed": false`. Repo checkouts and
  project-overlay rules are never flagged (fail-open);
  `POLYMATH_INSTALLED_PLUGINS` pins the set for tests. Locked by the
  route-eval `partial-install` category, gated in ROUTE-EVAL-1.
- **Deterministic shortlist consumer (`--shortlist`).**
  `route-hint.py --shortlist "<text>"` prints the top-3 scored
  candidates as JSON — including sub-threshold ones, each flagged
  `fires` when it matched a hard signal above the ambient threshold —
  and `/polymath-core:route` gains a step 0 that reads it as the
  constrained choice set (reason inside the top-3 first; route outside
  a non-empty shortlist only with a stated reason). The held-out eval
  reports the matching `constrained` block (top-3 hit rate on
  naturalistic cases) in route-metrics.json — reported, not gated.
- **Routing schema v1 consumed end-to-end.** `route-hint.py` honors
  `not_intents` (a matching phrase vetoes the surface before scoring)
  and `repo_state` (+1 soft boost from cached repo evidence — never
  satisfies the hard-signal firing requirement; the why-line names
  "repo state"); project overlay rules may carry both.
  `event-trigger.py` is now data-driven: rules come from the compiled
  `events` list in `data/route-signals.json` (declared per surface in
  routing.yaml sidecars) — the hardcoded table is gone. New
  `write-repo-evidence.py` SessionStart step caches declared repo-state
  probes (≤64, 200ms budget, fail-open; exact path / `dir/` / glob
  semantics) into `repo-evidence.json`, honored only when its recorded
  root matches the current repo.
- **Doctor reports the routing pipeline.** `doctor.sh` gains a
  *Routing pipeline* section: resolved `routing.mode`, routing config
  errors (flow-style / unknown values), an engaged kill switch, and
  recent decision events for this root (enforce denials, fail-opens,
  kill-switch uses, rejected marks) via the sibling
  `polymath-pipeline status` — with a warning when that plugin is not
  installed and `classify`/`enforce` declarations would be inert.
- **`initialize-project` authors the routing posture.** Step 4 now
  writes an explicit `routing:` block — `mode: classify` by default,
  `enforce` offered, `hint` as the zero-ceremony opt-out — and the
  onboarding doc names the declared mode and adds `polymath-pipeline`
  to the install set when classify/enforce is chosen. Strictness is a
  written, reviewable line, never ambient.
- **Opt-in visibility markers (`attribution` consumed).** The
  `project-context` contract now defines: `chat_markers: true` makes
  localizing skills prefix their primary chat-visible output with an
  origin marker (`[polymath:<plugin>:<skill>]`); default off keeps
  today's unmarked output. `commit_trailer` is consumed by
  `polymath-release:commit`.
- **`provenance` project.yaml key** (`runs: true|false`, default off) —
  schema + loader (KNOWN_TOP_KEYS) for the runner's opt-in run
  provenance; drift-gated like every other key.
- **Tracker consumption contract.** `project-context` now documents how
  item-creating skills consume the `tracker` block: destination
  defaults, 3-layer provenance marking (title prefix, tag, traceability
  footer), post-create readback verification, and HITL-only pushes.
- **Project routing overlay.** The route-hint hook reads
  `.polymath/route-signals.project.json` (found by the same cwd→repo-root
  walk as the mute marker) and scores its rules together with the bundled
  table: project rules win score ties and are labeled `project overlay`
  in the hint. Rules are sanitized on load — signal fields must be lists
  of strings, non-compiling `url`/`regex` patterns are dropped, `trust`
  is stripped (a project file can never claim auto-headless), rules
  without a `surface` or a signal are skipped — the overlay is capped at
  50 rules, and a malformed file is ignored entirely; project config can
  never break a turn. The SURFACE-2 uniqueness gate stays
  marketplace-internal; overlays may duplicate catalog intents and the
  scorer resolves them at runtime.
- **Convention-pack templates** under `templates/conventions/`
  (`knowledge-base`, `stack-doc`, `artifact-matrix`, `review-checklist`) —
  vendor-neutral skeletons any project or defaults pack fills in, including the
  `[VERIFY: …]` inferred-not-confirmed marker protocol. The
  `project-context` skill now defines the consumption contract
  (conventions_docs roles → wired consumer skills) and resolves the
  snapshot by glob, covering the per-plugin+marketplace data-dir layout.
- **Localization keys in the project schema** — shipped ahead of their
  consumers per `docs/plans/generalized-localization.md` (plan file since
  removed): `conventions_docs`
  (convention documents resolved by role, not filename), `smoke`
  (per-language boot-verification recipes for the planned `appStarts`
  gate), `tracker` (work-item destination + provenance marking; provider
  stays in `.polymath/capabilities.yaml`), `routing.mode`
  (`hint`/`classify`/`enforce`; only `hint` has shipped behavior),
  `attribution` (chat markers + commit trailer), `artifact_matrix`
  (path to a work-type × scope artifact-requirements doc), and `prompts`
  opened to the full 11-artifact template vocabulary. The loader
  validates surface shape (`routing.mode` enum, `smoke.*.start`
  required, mapping types) and the drift gate pins it to the schema.
- **Machine-local config overlay.** `./.polymath/project.local.yaml`
  (gitignored) deep-merges on top of the resolved `project.yaml`: mappings
  merge per key with the overlay winning, lists and scalars are replaced.
  Fail-open — a malformed or invalid overlay is warned and skipped, never
  failing the session; a valid overlay can serve as the sole source when no
  base file resolves. `_meta.overlay` records the applied path.
- **Ambient routing hint** (`UserPromptSubmit` hook). `route-hint.sh` /
  `route-hint.py` extract deterministic signals from the prompt (URLs,
  CVE/GHSA keys, mentioned paths, inline diffs, intent phrasings), score them
  against the bundled `data/route-signals.json` table, and — only when a *hard*
  signal is present — emit one quiet line proposing the smallest matching
  surface. Detect → propose → confirm; never auto-runs. Intent phrasing alone
  never fires (false-positive guard). Suppress with `POLYMATH_ROUTE_MUTE=1` or a
  `.polymath/route-muted` marker. Moves routing from pull (`/route`) to push.
  Tested by `tools/route-triggering.py` (deterministic, no model) and wired into
  `conformance.sh --all` as the `ROUTE-TRIGGER` gate.
- `route` skill and `/route` command to select the right Polymath
  workflow, skill, connector, agent, or external catalog for a prompt,
  returning JSON with confidence, evidence, alternatives, and the next
  action.
- `initialize-project` skill and `/init-project` command to generate
  `.polymath/project.yaml`, capability mappings, and onboarding notes
  from an existing repository.
- Project-context schema support for `setup:` and `polymath:` activation
  metadata, including required tools, environment variable names,
  recommended plugins, workflows, and compatible agent surfaces.

### Changed

- **Unknown top-level keys in `project.yaml` warn instead of failing.**
  The loader drops unrecognized keys (recorded in `_meta.ignored_keys`)
  rather than exiting 2 and withholding the snapshot, so a config written
  for a newer schema degrades gracefully on an older loader. A drift-gate
  unit test now pins the loader's key list to
  `registry/schemas/project.schema.json`.

### Removed

- **`mcp_servers` project key.** Declared-but-never-consumed; capability →
  provider/plugin selection is owned by `.polymath/capabilities.yaml`.
  Existing files declaring it now get a warning and the key is ignored.

## [0.1.0]

### Added

- `conventions` skill — load Polymath naming, token-budget, hook, and
  workflow conventions on demand.
- `glossary` skill — common Polymath / SDLC terms in one place.
- `project-context` skill — exposes the resolved `.polymath/project.yaml`
  snapshot to other skills.
- SessionStart hook (`hooks/scripts/session-start.sh`) that loads the
  project context, then surfaces any paused `polymath-flows` workflow
  runs plus any due items from the scheduled-work queue.
- Project-context loader at `hooks/scripts/load-project-context.py`
  reads `.polymath/project.yaml` (project →
  `${CLAUDE_CONFIG_DIR}` → home), validates against
  [`registry/schemas/project.schema.json`](../../registry/schemas/project.schema.json),
  and writes the resolved snapshot to
  `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json`.
- `/plugin-budget` command — thin alias for the budget reporter.
- `references/scheduled-queue.md` documenting the queue.json contract
  external schedulers can write to.
