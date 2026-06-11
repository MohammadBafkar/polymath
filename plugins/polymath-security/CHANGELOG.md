# Changelog — polymath-security

## [Unreleased]

### Added

- **Summary-first checkpoint.** `stride-threat-model` confirms scope,
  trust boundaries, and the highest-risk STRIDE candidates on one screen
  before drafting the full model.
### Changed

- `supply-chain-review` skill folded in from the former `polymath-supply-chain` plugin — SBOM/SLSA/provenance are appsec.

## [0.1.0]

### Added

- Initial v0.1 components: `stride-threat-model` skill (writes a Threat-model artifact validated by the ThreatModel JSON schema) and `owasp-review` skill (diff-driven Top 10 review keyed to file:line).
- Ships `Threat-model.md` template under `templates/`.
