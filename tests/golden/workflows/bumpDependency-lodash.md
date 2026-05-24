---
workflow: bumpDependency
scenario: bumpDependency-lodash
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-connector-snyk:triage-vulns
    - polymath-engineering:read-code
    - polymath-engineering:feature-dev
    - polymath-engineering:code-review
    - polymath-engineering:verify-change
  artifacts:
    - "docs/dep-bumps/lodash-bump-vulns.md"
  state_must_pass:
    - vulns-doc-exists
    - verify-mentions-tests
    - review-checks-scope
timeout_seconds: 600
---

# Prompt

> Bump lodash to close the open critical Snyk finding.

/polymath-flows:run-workflow bumpDependency dependency="lodash" targetVersion="4.17.21"

# Acceptance

- Snyk triage doc shows the LODASH critical was REACHABLE and is closed
  by 4.17.21.
- Orient step lists the call sites of lodash in this codebase.
- Bump step makes the SMALLEST diff: no opportunistic refactor of unrelated
  code; only the minimum required for the version bump.
- Review surfaces "scope creep" check.
- Verify confirms tests pass + the Snyk finding is closed.
