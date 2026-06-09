---
plugin: polymath-security
skill: supply-chain-review
trigger_prompts:
  - "review our software supply-chain posture before the enterprise launch"
  - "we need an SBOM and dependency provenance check"
  - "audit our dependencies for license compliance and signing"
must_invoke:
  - polymath-security:supply-chain-review
allow_invoke:
  - polymath-security:*
  - polymath-security:*
  - polymath-vuln-scan:*
  - polymath-core:*
forbidden_prompts:
  - "triage this specific CVE in our running service"
  - "bump lodash to the latest version safely"
---

# Why this test exists

SBOM/provenance/license/SLSA phrasings route here. Forbidden prompts guard
against `polymath-vuln-scan:triage-vulns` (runtime CVE) and the
`bumpDependency` workflow.
