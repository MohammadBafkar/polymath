# polymath-core

Foundation plugin for the Polymath marketplace. Implicit dependency of everything in tier 1+.

## What it ships

- Skills: `conventions`, `glossary`, `project-context`.
- Commands: `/plugin-budget`.
- Hooks: `SessionStart` — loads `.polymath/project.yaml` (see [`docs/PROJECT-LOCALIZATION.md`](../../docs/PROJECT-LOCALIZATION.md)) into `$CLAUDE_PLUGIN_DATA/polymath-core/project-context.json`, then surfaces paused workflows (quiet otherwise).

## Installation

```bash
claude plugin install polymath-core@polymath
```

## Why this plugin exists

Polymath uses a foundation plugin to keep cross-cutting context (naming, token budget, commands-vs-skills, workflow vocabulary) out of every other plugin's body. Other plugins can `Skill` into `conventions` or `glossary` instead of duplicating the rules.

## License

Apache-2.0.
