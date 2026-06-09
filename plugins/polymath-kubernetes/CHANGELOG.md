# Changelog — polymath-kubernetes

## [0.1.0]

### Added

- Initial v0.1 components: `write-manifest`, `audit-rbac-grants`, `propose-pod-security-standards` skills.
- Hook: `PreToolUse(Bash)` blocks mutating kubectl commands on prod-named contexts; bypass via `POLYMATH_ACK_PROD` token.
