# Changelog — polymath-author

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
