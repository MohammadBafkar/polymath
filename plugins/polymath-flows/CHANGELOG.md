# Changelog — polymath-flows

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `run-workflow`, `resume-workflow`, `list-workflows`: runner path resolves under Claude Code (`${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}`, quoted).
- `run-workflow`: removed the instruction to pad step summaries with gate words; steps load the invoked skill and fail when it isn't installed; artifacts are checked before `complete`; `fail --summary` takes inline text; `auto-headless` never applies to workflows.
- SessionStart: the documented index-mute marker under `~/.polymath/data` is honored under Claude Code.

## [0.8.0]

flows-lite workflow runner: deterministic serial executor with state, resume, and mustPass checks.

### Skills

- **list-workflows** — List active, paused, and completed flows-lite workflow runs from the local plugin data directory.
- **resume-workflow** — Resume a paused flows-lite workflow run from the last completed step using bin/polymath-flow resume.
- **run-workflow** — Run a flows-lite workflow end-to-end; the skill drives the loop while bin/polymath-flow owns YAML validation, state, and mustPass checks.
