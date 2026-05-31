---
plugin: polymath-supply-chain
scenario: supply-chain-review-pre-release
expect:
  invoked:
    - polymath-supply-chain:supply-chain-review
  output_matches:
    - "SBOM"
    - "license"
  not_invoked:
    - polymath-connector-snyk:triage-vulns
timeout_seconds: 90
---

# Prompt

> Before we ship 1.0 to enterprise customers, review our software
> supply-chain posture — they'll ask for an SBOM and provenance.

Use polymath-supply-chain:supply-chain-review.

# Acceptance

- SBOM presence/completeness assessed; pinning/provenance and registry trust reviewed.
- License audit against policy; signing/SLSA attestation coverage evaluated.
- Findings ranked with concrete remediations; compliance controls mapped where in scope.
