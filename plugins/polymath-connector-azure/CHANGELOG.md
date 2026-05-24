# Changelog — polymath-connector-azure

## [Unreleased]

### Added

- Initial v0.1 components: `inspect-azure-resource` skill (ARM ID → describe + role-assignments + can-i + activity-log writes + cost ping); `references/azure-tools.md`.
- `userConfig.azureSubscription` and `userConfig.azureLocation`.
- `polymath-cli-only` keyword: no .mcp.json, uses the local `az` CLI.
