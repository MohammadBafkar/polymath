# Changelog — polymath-connector-aws

## [Unreleased]

### Added

- Initial v0.1 components: `inspect-aws-resource` skill (ARN → describe + simulate-principal-policy + CloudTrail + Cost Explorer); `references/aws-tools.md`.
- `userConfig.awsProfile` and `userConfig.awsRegion` (non-sensitive — auth comes from the local `~/.aws/` config).
- `polymath-cli-only` keyword: no .mcp.json, uses the local `aws` CLI.
