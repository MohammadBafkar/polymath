---
workflow: weeklyReleaseTrain
scenario: weeklyReleaseTrain-v1.4.0
expect:
  invoked:
    - polymath-flows:run-workflow
    - polymath-engineering:read-code
    - polymath-release:changelog
    - polymath-release:release-notes
    - polymath-engineering:verify-change
    - polymath-content:write-advisory
    - polymath-release:pr
  artifacts:
    - "docs/release-notes/v1.4.0-survey.md"
    - "docs/release-notes/v1.4.0.md"
    - "docs/release-notes/v1.4.0-internal.md"
    - "docs/pr/v1.4.0.md"
    - "CHANGELOG.md"
  state_must_pass:
    - survey-exists
    - release-notes-exists
    - release-notes-has-headline
    - internal-advisory-exists
    - verify-mentions-tests
    - tag-artifact-exists
timeout_seconds: 900
---

# Prompt

> Ship a weekly release-train candidate for v1.4.0.

/polymath-flows:run-workflow weeklyReleaseTrain version=v1.4.0 dryRun=no

# Acceptance

End-to-end: six steps run, every step writes a summary, all six
mustPass checks pass, and the run reaches state `completed` in
`${CLAUDE_PLUGIN_DATA}/workflows/<id>/state.json`. The release-notes
file has a headline, the internal-advisory is distinct from the
customer notes, and the tag PR is drafted (dryRun=no).

Then with `dryRun=yes`, the tag-pr step still produces a file but it's a
one-line "skipped" note rather than a full PR description.
