---
workflow: shipFeature
scenario: shipFeature-rate-limit-login
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-product:prd
    - polymath-product:acceptance-criteria
    - polymath-engineering:feature-dev
    - polymath-engineering:code-review
    - polymath-engineering:verify-change
    - polymath-release:changelog
    - polymath-release:pr
  artifacts:
    - "docs/prds/rate-limit-login.md"
    - "CHANGELOG.md"
    - "docs/pr/rate-limit-login.md"
  state_must_pass:
    - prd-exists
    - tests-mentioned
    - changelog-touched
    - pr-draft-exists
timeout_seconds: 900
---

# Prompt

> The shipFeature golden demo from PLAN.md sec 9.

/polymath-flows:run-workflow shipFeature title="Rate-limit /login" scope=small

# Acceptance

End-to-end: the workflow runs all seven steps, every step writes
a summary, all four mustPass checks pass, and the run reaches
state `completed` in `${CLAUDE_PLUGIN_DATA}/workflows/<id>/state.json`.

Then, in a second session, the workflow is resumable after a
mid-flow interrupt: `/polymath-flows:resume-workflow <id>`
picks up at the next pending step and finishes the run.
