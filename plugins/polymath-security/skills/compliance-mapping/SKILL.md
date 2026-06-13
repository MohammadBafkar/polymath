---
name: compliance-mapping
description: Map a compliance framework (SOC 2 / GDPR / ISO 27001 / HIPAA) to concrete technical controls and the evidence/artifacts each control needs for audit.
---

# compliance-mapping

> Auditors don't accept intentions; they accept evidence. Translate each framework requirement into a control someone owns and an artifact that proves it runs — or it isn't real.

## When to use

- Preparing for SOC 2 / ISO 27001 / GDPR / HIPAA, or mapping a requirement to engineering work.
- A control exists "in policy" but nobody can show it operates.
- A workflow invokes `polymath-security:compliance-mapping`.

Not this when: you are finding vulnerabilities (`owasp-review`) or modeling threats (`stride-threat-model`). Compliance maps requirements→controls→evidence; it is not a vuln hunt.

## Inputs

- The framework(s) in scope and the system/data boundary (what's in scope).
- Existing controls and where they're enforced.

## Procedure

1. **Define scope** precisely: which systems, data classes, and environments the audit covers. Out-of-scope must be justified and isolated.
2. **Pull the relevant control families**: e.g. SOC 2 Trust Services Criteria (Security/Availability/Confidentiality/…), ISO 27001 Annex A, GDPR articles (lawful basis, DSAR, breach notice, DPIA), HIPAA safeguards. Work from the actual criteria, not memory.
3. **Map each requirement → technical control**: access control (least privilege, MFA, review cadence), encryption (at rest/in transit — see `crypto-review`), logging/monitoring, change management, vulnerability management, backup/DR, vendor management, data retention/deletion.
4. **Name the evidence per control**: the artifact an auditor accepts — access-review records, CI logs showing the gate ran, config screenshots/IaC, ticket trails, signed policies, pen-test reports. A control with no evidence source is a finding waiting to happen.
5. **Assign an owner and cadence** to each control (who runs it, how often, where it's recorded). Automate evidence collection where possible.
6. **Gap analysis**: requirement with no control, or control with no evidence → remediation item with owner + date.
7. **Data-subject obligations** (GDPR/CCPA): lawful basis, consent records, DSAR/erasure workflow, processor agreements, breach-notification runbook.

## Output

- A control-mapping table: requirement → control → enforcement point → evidence artifact → owner → cadence, plus a gap list with remediation owners/dates.

## Quality bar

- Every in-scope requirement maps to a named control with a concrete evidence artifact.
- Each control has an owner and a cadence — not just a policy statement.
- Gaps are explicit remediation items with owners and dates.
- Scope boundaries (and exclusions) are stated and justified.
