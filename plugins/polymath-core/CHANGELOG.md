# Changelog — polymath-core

## [Unreleased]

### Added

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
