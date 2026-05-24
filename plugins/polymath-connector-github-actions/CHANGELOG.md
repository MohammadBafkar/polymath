# Changelog — polymath-connector-github-actions

## [Unreleased]

### Added

- Initial v0.1 components: `diagnose-ci-failure` skill; Stop hook that checks the latest run on the current branch via `gh` CLI and nudges on failure; `references/github-actions-tools.md`.
- No own MCP server — depends on `polymath-connector-github` which already exposes workflow tools.
