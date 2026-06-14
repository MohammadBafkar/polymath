# Changelog — polymath-flows

<!-- markdownlint-disable MD024 -->

## [0.8.0]

flows-lite workflow runner: deterministic serial executor with state, resume, and mustPass checks.

### Skills

- **list-workflows** — List active, paused, and completed flows-lite workflow runs from the local plugin data directory.
- **resume-workflow** — Resume a paused flows-lite workflow run from the last completed step using bin/polymath-flow resume.
- **run-workflow** — Run a flows-lite workflow end-to-end; the skill drives the loop while bin/polymath-flow owns YAML validation, state, and mustPass checks.
