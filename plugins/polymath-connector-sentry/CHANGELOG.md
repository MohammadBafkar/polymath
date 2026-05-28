# Changelog — polymath-connector-sentry

## [0.1.0]

### Added

- Initial v0.1 components: `.mcp.json` referencing a Sentry MCP server; `triage-error` skill (5-action classification: fix-now / fix-this-sprint / investigate / ignore-with-suppression / re-prioritize); UserPromptSubmit hook detecting Sentry URLs (short-IDs only when "Sentry" is in the prompt to avoid Jira-key collision); `references/sentry-tools.md`.
- `userConfig.sentryToken` (sensitive); `sentryOrg` required.
