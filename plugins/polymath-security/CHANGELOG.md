# Changelog — polymath-security

## [Unreleased]

### Changed

- `supply-chain-review` skill folded in from the former `polymath-supply-chain` plugin — SBOM/SLSA/provenance are appsec.

## [0.1.0]

### Added

- Initial v0.1 components: `stride-threat-model` skill (writes a Threat-model artifact validated by the ThreatModel JSON schema) and `owasp-review` skill (diff-driven Top 10 review keyed to file:line).
- Ships `Threat-model.md` template under `templates/`.
