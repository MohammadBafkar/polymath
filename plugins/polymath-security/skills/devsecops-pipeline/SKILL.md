---
name: devsecops-pipeline
description: Design security gates into CI/CD — SAST, DAST, SCA/dependency, secret, and IaC scanning — with severity thresholds, a triage flow, and noise control.
---

# devsecops-pipeline

> Security scanning that everyone ignores is theater. The skill is gating on what's exploitable, routing the rest to triage, and keeping false positives low enough that red means stop.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

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

```text
DevSecOps pipeline: refund-service (GitHub Actions, Python + Terraform)

Stage          Scanner (class)             Gate
PR             gitleaks (secrets)          block on any verified secret
PR             osv-scanner (SCA)           block: critical/high with a fix available AND reachable; else triage
PR             semgrep, diff-only (SAST)   block: high-confidence injection/auth rules; else comment
PR             checkov (IaC)               block: public buckets, open SGs, wildcard IAM
main/nightly   semgrep full, trivy image   triage queue; block release on critical with known exploit
nightly        ZAP baseline (DAST)         triage queue

Noise:     baseline at adoption; suppressions need justification + 90-day expiry; dedupe by CVE/rule across tools
Triage:    owner = CODEOWNERS of the path; SLA critical 7d · high 30d · medium 90d; override by AppSec lead, logged
Pipeline:  OIDC to cloud (no long-lived keys); actions pinned by SHA; protected main; SLSA provenance on images
Metrics:   MTTR by severity · escaped vulns per quarter · gate pass rate · false-positive rate
```

## Quality bar

- Gating is by severity AND exploitability/reachability, not raw finding count.
- Secret + dependency scanning run on every PR; heavier scans don't slow PRs.
- Suppressions require justification and expiry; false-positive rate is tracked.
- The CI pipeline itself is hardened (least-privilege tokens, pinned digests).
