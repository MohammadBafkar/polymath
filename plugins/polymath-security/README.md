# polymath-security

Security craft for the Polymath marketplace.

## What it ships

- Skills:
  - `stride-threat-model` — STRIDE threat model for a system/scope.
  - `owasp-review` — OWASP Top 10 review of a code diff.
  - `supply-chain-review` — dependency/release supply-chain risk.
  - `auth-design` — OAuth2/OIDC flow, token/session strategy, RBAC/ABAC, SSO, revocation.
  - `compliance-mapping` — SOC 2 / GDPR / ISO 27001 / HIPAA requirement → control → evidence.
  - `devsecops-pipeline` — SAST/DAST/SCA/secret/IaC scanning as CI gates with triage + noise control.
  - `crypto-review` — encryption at rest/in transit, key management + rotation, algorithm choice, foot-guns.
  - `llm-security-review` — OWASP LLM Top 10 audit: direct/indirect prompt injection, data leakage, insecure output, excessive agency.
- Templates: `Threat-model.md`.
- Workflows that invoke this plugin can validate the threat-model frontmatter with `mustPass: artifactValid` against the `ThreatModel` artifact schema.

## Installation

```bash
claude plugin install polymath-security@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
