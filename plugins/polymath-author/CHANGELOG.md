# Changelog — polymath-author

## [Unreleased]

### Added

- **`scaffold-component` skill** — scaffold a new component/service/module
  in the user's repo, convention-driven: read the `conventions_docs` shape
  docs, hand off to the stack's native generator (tool-spec handoff:
  compose and run `dotnet new` / `npm create` / `cargo new` / a repo-local
  generator instead of freehanding boilerplate), pull infra bodies from
  the owning skills (dockerize, ci-pipeline-github, write-manifest),
  never overwrite, finish with a regenerated prerequisites checklist.
- **`bin/gen-prerequisites.py`** — prerequisites-checklist generator: turns
  the project's `setup` block (context_sources, required_tools,
  environment, first_steps) into a markdown onboarding checklist;
  `--check` runs each tool's check command and exits 1 when a REQUIRED
  tool fails. Env var values are never read or printed.
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
