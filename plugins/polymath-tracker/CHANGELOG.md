# Changelog — polymath-tracker

## [Unreleased]

### Changed

- Renamed from `polymath-connector-jira` and merged `polymath-connector-linear`
  into a single `issue_tracker` umbrella connector (mirrors
  `polymath-connector-monitoring`). Ships both the Jira and Linear MCP servers
  (each activated by its own credentials), both detect hooks, and the
  `jira-triage` / `linear-triage` skills. The two providers' colliding
  `file-bug-from-incident`
  skills were unified into one provider-agnostic skill that resolves Jira vs
  Linear from `${capabilities.issue_tracker.provider}`. The capability
  vocabulary now maps both `jira` and `linear` → `polymath-tracker`.
  All `userConfig` keys are optional — supply the set for your tracker.

## [0.1.0]

### Added

- Initial v0.1 components: `.mcp.json` referencing an Atlassian MCP server; `jira-triage` + `file-bug-from-incident` skills; UserPromptSubmit ticket-key detection hook (matches `PROJ-123` and `*.atlassian.net/browse/...`); `references/jira-tools.md`.
- `userConfig` for `jiraUrl`, `jiraEmail`, `jiraApiToken` (sensitive).
