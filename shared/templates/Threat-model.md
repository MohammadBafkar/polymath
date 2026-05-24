---
artifact: ThreatModel
schemaVersion: 0.1
system: "{{system}}"
scope: "{{scope}}"
owner: "{{owner}}"
created: "{{date}}"
stride_categories:
  - Spoofing
  - Tampering
  - Repudiation
  - InformationDisclosure
  - DenialOfService
  - ElevationOfPrivilege
data_classification: internal
---

# Threat model: {{system}}

## Scope

What is in scope for this model. Reference the PRD or ADR that motivated it.

## Data flow

A short diagram (mermaid or ASCII) showing the trust boundaries the system spans.

## Assumptions

What we assume the platform / surrounding system already provides.

## Threats by STRIDE category

### Spoofing

| # | Threat | Mitigation | Owner |
| - | ------ | ---------- | ----- |
| S1 | … | … | … |

### Tampering

…

### Repudiation

…

### Information disclosure

…

### Denial of service

…

### Elevation of privilege

…

## Open questions

- …

## References

- PRD: `{{prd_link}}`
- Related ADRs: …
