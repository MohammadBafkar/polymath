---
plugin: polymath-release
scenario: changelog-from-diff
expect:
  invoked:
    - polymath-release:changelog
  artifacts:
    - "CHANGELOG.md"
  not_invoked:
    - polymath-release:pr
timeout_seconds: 90
---

# Prompt

> Update CHANGELOG.md from the current diff.

The current diff adds a new /healthz endpoint that returns 200 OK
with a JSON body of `{"status":"ok","version":"<x>"}`. There are no
breaking changes. Update CHANGELOG.md under [Unreleased].

# Acceptance

- CHANGELOG.md exists and has an `## [Unreleased]` section.
- A bullet under `### Added` mentions the /healthz endpoint and the
  JSON body in user-facing language.
- No emoji in the bullet.
- The bullet does not restate the implementation detail
  (e.g. which file changed); it describes user-visible behavior.
