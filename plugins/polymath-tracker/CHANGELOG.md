# Changelog — polymath-tracker

## [Unreleased]

### Added

- All three skills consume the project's `tracker` block
  (`polymath-core:project-context` contract): destination defaults
  (`project`/`area_path`/`iteration`, `work_item_types`), 3-layer
  provenance marking on every created item (title prefix, tag,
  traceability footer), post-create readback verification, and HITL-only
  pushes — `file-bug-from-incident` presents the full ticket set for one
  explicit confirmation before any create call.

### Changed

- One `issue_tracker` umbrella plugin: ships both the Jira and Linear MCP
  servers (each activated by its own credentials), both detect hooks, and the
  `jira-triage` / `linear-triage` skills. A single provider-agnostic
  `file-bug-from-incident` skill resolves Jira vs Linear from
  `${capabilities.issue_tracker.provider}`. The capability vocabulary maps both
  `jira` and `linear` → `polymath-tracker`. All `userConfig` keys are optional —
  supply the set for your tracker.

## [0.1.0]

### Added

- Initial v0.1 components: `.mcp.json` referencing an Atlassian MCP server; `jira-triage` + `file-bug-from-incident` skills; UserPromptSubmit ticket-key detection hook (matches `PROJ-123` and `*.atlassian.net/browse/...`); `references/jira-tools.md`.
- `userConfig` for `jiraUrl`, `jiraEmail`, `jiraApiToken` (sensitive).
