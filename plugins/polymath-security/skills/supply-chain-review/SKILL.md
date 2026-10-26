---
name: supply-chain-review
description: Review supply-chain integrity — SBOM, dependency provenance/lockfiles, license audit, signing/SLSA attestation, build trust. Supply-chain posture, not runtime vuln triage (triage-vulns).
---

# supply-chain-review

> The exploit you don't write is the dependency you didn't vet. Review what enters the build and whether you can prove where it came from.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A release, audit, or compliance ask needs assurance about *what's in the build and where it came from*.
- The user asks about SBOM, provenance, signing, SLSA, license compliance, or supply-chain risk.
- A workflow invokes `polymath-security:supply-chain-review`.

This reviews *supply-chain posture*. It is not triaging a specific runtime CVE (`polymath-vuln-scan:triage-vulns`), bumping one dependency (the `bumpDependency` workflow), or app-code threat modeling (`polymath-security:stride-threat-model`).

## What to review

- **SBOM** — is one generated (CycloneDX/SPDX) per build, complete (transitive), and stored with the artifact?
- **Provenance & lockfiles** — pinned, hash-locked dependencies; lockfile committed; no floating ranges in production builds; resolved from a trusted registry/mirror.
- **License compliance** — every dependency's license known; copyleft/incompatible licenses flagged against the project's policy.
- **Build integrity** — hermetic/reproducible build? CI that produces releases is trusted, least-privilege, and not running untrusted PR code with secrets.
- **Signing & attestation** — artifacts signed (Sigstore/cosign); SLSA provenance attestation; consumers can verify.
- **Dependency hygiene** — unmaintained/single-maintainer critical deps, typosquat risk, dependency confusion (internal names resolvable from public registries).
- **Control mapping** — map findings to the relevant controls (SOC 2, SSDF, GDPR processor obligations) where compliance is in scope.

## Inputs

- The repository or release under review (required): manifests, lockfiles, CI config, release workflow.
- The project's license policy (optional) — absent: flag copyleft/unknown licenses for review rather than declaring them violations.
- Compliance scope (optional): SOC 2 / SSDF / customer requirements that make findings mandatory.

## Procedure

1. Establish whether an SBOM exists and is complete; generate/recommend one if not.
2. Audit pinning/lockfiles and registry trust; flag floating or unverified sources.
3. Run the license audit against policy; flag incompatible/unknown licenses.
4. Assess build-pipeline trust and signing/attestation coverage.
5. Flag risky dependencies (unmaintained, typosquat, confusion).
6. Map material findings to in-scope compliance controls.
7. Output findings ranked by exploitability/compliance impact, each with a remediation.

## Output

Findings ranked by exploitability, then compliance impact:

```text
Supply-chain review: refund-service v2.4.0

SBOM:        none produced → [HIGH] generate CycloneDX per build (syft) and attach to the release
Lockfiles:   poetry.lock committed, hashes present        OK
             Dockerfile `pip install requests` unpinned → [MEDIUM] pin + hash or install from the lock
Registry:    internal package `refund-common` resolvable from public PyPI → [HIGH] dependency confusion: reserve the name / use a scoped index
Licenses:    1 AGPL-3.0 (pdfgen 1.2) vs policy "no network copyleft" → [MEDIUM] replace or get a legal exception
Build:       release job runs on pull_request_target with secrets → [HIGH] split: untrusted PR code never sees secrets
Signing:     images unsigned, no provenance → [MEDIUM] cosign keyless + SLSA provenance attestation
Hygiene:     `left-padx` single-maintainer, last release 2019 → [LOW] vendor or replace

Controls:    SSDF PS.3.2 (SBOM), PO.3.2 (build integrity) — both currently unmet
```

## Quality bar

- SBOM presence/completeness is assessed, not assumed.
- Findings distinguish "no SBOM/provenance" (posture) from "this CVE" (runtime triage — out of scope here).
- License findings name the offending dependency + license + policy conflict.
- Each finding has a concrete remediation (pin, sign, replace, attest), not "improve supply-chain security".
