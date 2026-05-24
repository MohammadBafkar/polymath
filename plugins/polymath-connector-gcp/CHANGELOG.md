# Changelog — polymath-connector-gcp

## [Unreleased]

### Added

- Initial v0.1 components: `inspect-gcp-resource` skill (resource path → describe + IAM policy + test-iam-permissions + audit-log + cost ping); `references/gcp-tools.md`.
- `userConfig.gcpProject` and `userConfig.gcpRegion`.
- `polymath-cli-only` keyword: no .mcp.json, uses the local `gcloud` CLI.
