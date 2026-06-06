# Changelog — polymath-core

## [Unreleased]

### Added

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
  [`shared/schemas/project.schema.json`](../../shared/schemas/project.schema.json),
  and writes the resolved snapshot to
  `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json`.
- `/plugin-budget` command — thin alias for the budget reporter.
- `references/scheduled-queue.md` documenting the queue.json contract
  external schedulers can write to.
