# Changelog — polymath-author

## [Unreleased]

### Added

- `/new-org-pack` command + `bin/new-org-pack.sh`: scaffold a standalone
  organization pack — a company-side marketplace with one
  `<org>-conventions` plugin carrying an `org-defaults` copy-in skill
  (detected by `polymath-core:init-project`), a starter `.polymath/`
  config with a `conventions_docs` role map, and a conventions corpus
  seeded from polymath-core's skeletons (same-marketplace symlink,
  dereferenced at install). Nothing org-specific ships in this catalog.

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
