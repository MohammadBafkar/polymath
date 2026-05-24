# Changelog — polymath-connector-linear

## [Unreleased]

### Added

- Initial v0.1 components: `.mcp.json` referencing a Linear MCP server; `linear-triage` skill (Linear-aware workflow-state IDs + cycle assignment + people-not-teams assignee rule); `file-bug-from-incident` skill (postmortem → Linear issues with sev-mapped priority + bidirectional backlinks); UserPromptSubmit hook detecting Linear keys (only when "Linear" is mentioned, to avoid Jira-key collision); `references/linear-tools.md`.
- `userConfig.linearApiKey` (sensitive).
