# Changelog — polymath-kubernetes

## [0.7.0]

### Changed

- Version aligned to 0.7.0 as part of the marketplace-wide 0.7.0 release; no functional change to this plugin.

## [0.1.0]

### Added

- Initial v0.1 components: `write-manifest`, `audit-rbac-grants`, `propose-pod-security-standards` skills.
- Hook: `PreToolUse(Bash)` blocks mutating kubectl commands on prod-named contexts; bypass via `POLYMATH_ACK_PROD` token.
