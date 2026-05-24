---
workflow: featureFromIdea
scenario: featureFromIdea-bulk-refunds
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-research:interview-guide
    - polymath-research:persona
    - polymath-product:prd
    - polymath-product:acceptance-criteria
    - polymath-engineering:feature-dev
    - polymath-engineering:code-review
    - polymath-engineering:verify-change
    - polymath-release:changelog
    - polymath-release:pr
  artifacts:
    - "docs/research/bulk-refunds-guide.md"
    - "docs/prds/bulk-refunds.md"
    - "CHANGELOG.md"
    - "docs/pr/bulk-refunds.md"
  state_must_pass:
    - interview-guide-exists
    - prd-exists
    - tests-mentioned
    - changelog-touched
    - pr-draft-exists
timeout_seconds: 1200
---

# Prompt

> Ship the bulk refunds feature from discovery to PR draft.

/polymath-flows:run-workflow featureFromIdea title="Bulk refunds" researchQuestion="What makes high-volume merchants give up on the refunds workflow?" scope=small

# Acceptance

- Interview guide is Mom-Test-shaped (past behavior, target N ≥ 5,
  avoid-list present).
- If interviews haven't actually run, persona step pauses with that
  explicit message — the workflow refuses to draft a PRD on assumptions.
- PRD references the persona doc explicitly.
- Acceptance criteria tie each to a persona behavior the interviews
  surfaced.
- Final PR draft links the persona doc + the PRD.
