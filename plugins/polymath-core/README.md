# polymath-core

Foundation plugin for the Polymath marketplace. Implicit dependency of everything in tier 1+.

## What it ships

- Skills: `route`, `conventions`, `glossary`, `initialize-project`, `project-context`, `doctor`.
- Commands: `/route`, `/init-project`, `/plugin-budget`, `/doctor`.
- Hooks:
  - `SessionStart` — loads `.polymath/project.yaml` (see [`docs/PROJECT-LOCALIZATION.md`](../../docs/PROJECT-LOCALIZATION.md)) into `$CLAUDE_PLUGIN_DATA/polymath-core/project-context.json`, then surfaces paused workflows. When a repo has no project file it emits a single suppressible nudge toward `/init-project`; otherwise quiet.
  - `UserPromptSubmit` — ambient routing hint. Extracts deterministic signals from the prompt (URLs, CVE/GHSA keys, mentioned paths, inline diffs, intent phrasings) via `data/route-signals.json` and, only when a *hard* signal is present, prints one quiet line proposing the smallest matching surface. Detect-only — never auto-runs; intent phrasing alone never fires. Suppress with `POLYMATH_ROUTE_MUTE=1` or a `.polymath/route-muted` marker. Confirm a proposal with `/route`.

## Installation

```bash
claude plugin install polymath-core@polymath
```

## Why this plugin exists

Polymath uses a foundation plugin to keep cross-cutting context (routing, naming, token budget, commands-vs-skills, workflow vocabulary) out of every other plugin's body. Other plugins can `Skill` into `route`, `conventions`, or `glossary` instead of duplicating the rules.

## License

MIT.
