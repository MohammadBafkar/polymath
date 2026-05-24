---
workflow: securityFinding
scenario: securityFinding-idor-on-refunds
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-security:owasp-review
    - polymath-engineering:feature-dev
    - polymath-engineering:code-review
    - polymath-engineering:verify-change
  artifacts:
    - "docs/security/idor-on-refunds-owasp.md"
  state_must_pass:
    - owasp-exists
    - owasp-cites-file-line
    - implement-cites-finding
    - verify-mentions-tests
timeout_seconds: 600
---

# Prompt

> Address this security finding.

/polymath-flows:run-workflow securityFinding title="IDOR on refunds" severity=high scope="api/refunds.py"

A penetration test report says GET /v1/orders/<order_id>/refunds returns
refunds for any order_id with no ownership check.

# Acceptance

- OWASP review cites file:line for the IDOR finding (A01 Broken Access Control).
- For high severity, the STRIDE threat-model step is executed (not skipped).
- Implementation cites the finding ID in its commit body / summary.
- Verify confirms the regression test fails against the old (vulnerable) code.
