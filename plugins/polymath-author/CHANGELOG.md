# Changelog — polymath-author

## [Unreleased]

### Added

- `/new-pack` command + `bin/new-pack.sh`: scaffold a defaults pack — a
  standalone marketplace of per-scope conventions plugins (organization,
  team, product line, or project archetype). Each plugin carries an
  `apply-defaults` copy-in skill (detected by
  `polymath-core:init-project`), a starter `.polymath/` config with a
  `conventions_docs` role map, and a conventions corpus seeded from
  polymath-core's skeletons (same-marketplace symlink, dereferenced at
  install). Re-running against an existing pack ADDS a scope plugin;
  stacking rule: narrowest scope first, since apply-defaults never
  overwrites. Nothing scope-specific ships in this catalog.

## [0.1.0]

### Added

- `validate-plugin`, `token-budget-report`, `skill-author-critic` skills.
- Five scaffolders under `bin/`: `new-plugin.sh`, `new-skill.sh`,
  `new-connector.sh`, `new-command.sh`, `new-workflow.sh`. Each walks
  up from the caller's cwd to find the marketplace root, so the
  scripts work in any project where `polymath-author` is installed.
- Bundled `templates/Workflow.yaml` for the workflow scaffolder.
- Five thin-alias commands invoking the bundled scaffolders:
  `/new-plugin`, `/new-skill`, `/new-connector`, `/new-workflow`,
  `/new-command`.
- References: `skill-style-guide.md`, `frontmatter-cheatsheet.md`.
