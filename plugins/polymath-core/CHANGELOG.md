# Changelog — polymath-core

## [Unreleased]

### Added

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
