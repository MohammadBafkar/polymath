---
plugin: polymath-security
scenario: stride-for-refund-service
expect:
  invoked:
    - polymath-security:stride-threat-model
  artifacts:
    - "docs/threat-models/refund-service.md"
  output_matches:
    - "Spoofing"
    - "Tampering"
    - "Elevation of [pP]rivilege"
  not_invoked:
    - polymath-security:owasp-review
timeout_seconds: 120
---

# Prompt

> Threat-model the refund-service.

Use polymath-security:stride-threat-model. System: refund-service.
Scope: refund creation + state transitions + downstream payment-provider
calls. Owner: payments team.

# Acceptance

- docs/threat-models/refund-service.md exists with ThreatModel frontmatter
  (artifact: ThreatModel; stride_categories present).
- At least one threat (or an explicit "doesn't apply because") per STRIDE category.
- Every threat has an owner (team) and a mitigation that is observable.
- No mitigation is "be careful" or "review carefully".
