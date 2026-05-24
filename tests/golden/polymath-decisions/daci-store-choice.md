---
plugin: polymath-decisions
scenario: daci-store-choice
expect:
  invoked:
    - polymath-decisions:daci
  artifacts:
    - "docs/decisions/rate-limit-store.md"
  output_matches:
    - "Driver"
    - "Approver"
    - "(Contributor|Informed)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Run a DACI on the rate-limit store choice.

Use polymath-decisions:daci. Title: "Rate-limit store choice". Driver:
@alice. Approver: VP Eng. Deadline: end of next sprint.

# Acceptance

- docs/decisions/rate-limit-store.md exists with DACIDecision frontmatter.
- Exactly one Approver; Approver ≠ Driver.
- Contributors and Informed sections are filled (or explicitly "(none)").
- Decision and Rationale sections start empty (Driver may not pre-fill).
- A real deadline is set; "soon" or "TBD" rejected.
