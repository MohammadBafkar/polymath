# Changelog — polymath-security

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Changed

- `owasp-review`: walks the OWASP Top 10:2025 (was the 2021 list while claiming "current"); traces source → sink before reporting.
- `llm-security-review`: exfiltration channels and the private-data + untrusted-content + outbound-channel combination; PoCs only where authorized.
- `auth-design`: refresh-token rotation with reuse detection, sender-constrained tokens, no tokens in `localStorage`, passkeys.
- `crypto-review`: post-quantum hybrid key exchange note; `compliance-mapping`: not legal advice.

### Fixed

- `supply-chain-review` description pointed at a nonexistent `snyk:triage-vulns`.

## [0.8.0]

Security craft: STRIDE, OWASP review, supply-chain, auth design, compliance mapping, DevSecOps pipeline, crypto review, LLM-security audit.

### Skills

- **auth-design** — Design authentication/authorization — OAuth2/OIDC flow choice, JWT vs opaque/session tokens, RBAC vs ABAC, SSO, token lifetime/refresh/revocation.
- **compliance-mapping** — Map a compliance framework (SOC 2 / GDPR / ISO 27001 / HIPAA) to concrete technical controls and the evidence/artifacts each control needs for audit.
- **crypto-review** — Review a cryptography choice — encryption at rest/in transit, key management + rotation, algorithm/mode selection, and common foot-guns (IV reuse, ECB, home-rolled crypto).
- **devsecops-pipeline** — Design security gates into CI/CD — SAST, DAST, SCA/dependency, secret, and IaC scanning — with severity thresholds, a triage flow, and noise control.
- **llm-security-review** — Audit an LLM system for security — OWASP LLM Top 10, direct/indirect prompt injection, sensitive-data leakage, insecure output handling, RAG and agent-action risks.
- **owasp-review** — Review a code diff against the current OWASP Top 10; report findings keyed to file:line with severity (high/medium/low) and a fix recommendation.
- **stride-threat-model** — Model a system with STRIDE; writes docs/threat-models/<slug>.md with frontmatter validated by the ThreatModel artifact schema.
- **supply-chain-review** — Review supply-chain integrity — SBOM, dependency provenance/lockfiles, license audit, signing/SLSA attestation, build trust. Supply-chain posture, not runtime vuln triage (snyk:triage-vulns).
