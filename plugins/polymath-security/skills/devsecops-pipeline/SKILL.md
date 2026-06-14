---
name: devsecops-pipeline
description: Design security gates into CI/CD — SAST, DAST, SCA/dependency, secret, and IaC scanning — with severity thresholds, a triage flow, and noise control.
---

# devsecops-pipeline

> Security scanning that everyone ignores is theater. The skill is gating on what's exploitable, routing the rest to triage, and keeping false positives low enough that red means stop.

## When to use

- Adding or rationalizing security scanning in CI/CD.
- Scanners exist but are noisy, advisory-only, or block on findings nobody fixes.
- A workflow invokes `polymath-security:devsecops-pipeline`.

Not this when: you are reviewing one diff by hand (`owasp-review`), triaging a specific vuln (`polymath-vuln-scan:triage-vulns`), or assessing dependencies for a release (`supply-chain-review`). This designs the pipeline.

## Inputs

- The stack/languages, the CI system, and the current scanning (if any).
- Risk tolerance and where the app is exposed.

## Procedure

1. **Pick the scanner classes** to the stack:
   - *SAST* — static code analysis for code-level flaws (injection, unsafe APIs).
   - *SCA / dependency scanning* — known-vuln (CVE) and license checks on dependencies + lockfile.
   - *Secret scanning* — pre-commit + CI, history-aware, to catch committed credentials.
   - *IaC scanning* — Terraform/K8s/Dockerfile misconfig (ties to `polymath-iac:policy-as-code`).
   - *DAST* — runtime scanning against a deployed/staging instance.
   - *Container image scanning* — base-image CVEs.
2. **Shift left, gate right**: fast checks (secret scan, SCA, SAST-diff) on PR; deeper checks (full SAST, DAST, image scan) on main/nightly so PRs stay fast.
3. **Set gate thresholds by severity + exploitability**: block on high/critical with a known exploit or reachable path; warn/triage on the rest. A wall of med/low advisories blocks nothing and trains people to ignore red.
4. **Control noise**: baseline existing findings, suppress with justification + expiry (not forever), and dedupe across tools. Track false-positive rate.
5. **Triage flow**: every non-gating finding routes to an owner + SLA by severity; integrate with the tracker. Define the break-glass/override (who approves, logged).
6. **Secure the pipeline itself**: least-privilege CI tokens, pinned action/image digests, protected branches, signed artifacts/provenance (SLSA).
7. **Measure**: mean-time-to-remediate by severity, escaped-vuln rate, gate pass rate.

## Output

- A one-page pipeline design: scanner classes mapped to PR vs main stages, gate thresholds by severity/exploitability, the noise-control + suppression policy, the triage flow + SLAs, pipeline-hardening controls, and the metrics.

## Quality bar

- Gating is by severity AND exploitability/reachability, not raw finding count.
- Secret + dependency scanning run on every PR; heavier scans don't slow PRs.
- Suppressions require justification and expiry; false-positive rate is tracked.
- The CI pipeline itself is hardened (least-privilege tokens, pinned digests).
