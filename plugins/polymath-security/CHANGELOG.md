# Changelog — polymath-security

## [0.7.0]

### Added

- Five skills closing the security-breadth gap (whetstone-coverage program, P4):
  `auth-design` (OAuth2/OIDC, tokens/sessions, RBAC/ABAC, SSO, revocation),
  `compliance-mapping` (SOC 2 / GDPR / ISO 27001 / HIPAA requirement→control→evidence),
  `devsecops-pipeline` (SAST/DAST/SCA/secret/IaC scanning as CI gates),
  `crypto-review` (encryption, key management, algorithm choice, foot-guns), and
  `llm-security-review` (OWASP LLM Top 10 audit — pairs with `polymath-ai:llm-guardrails`).
  Each declares a soft-tier `routing.yaml`.
- **Summary-first checkpoint.** `stride-threat-model` confirms scope,
  trust boundaries, and the highest-risk STRIDE candidates on one screen
  before drafting the full model.

### Changed

- `supply-chain-review` skill folded in from the former `polymath-supply-chain` plugin — SBOM/SLSA/provenance are appsec.

## [0.1.0]

### Added

- Initial v0.1 components: `stride-threat-model` skill (writes a Threat-model artifact validated by the ThreatModel JSON schema) and `owasp-review` skill (diff-driven Top 10 review keyed to file:line).
- Ships `Threat-model.md` template under `templates/`.
