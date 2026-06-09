---
plugin: polymath-vcs
scenario: open-pr-from-branch
expect:
  invoked:
    - polymath-vcs:open-pr
  output_matches:
    - "(create_pull_request|gh pr create|github MCP)"
    - "(base|main)"
  not_invoked:
    - polymath-vcs:triage-issue
timeout_seconds: 90
---

# Prompt

> Open a PR for my current branch.

Use polymath-vcs:open-pr. Branch is `feat/rate-limit-login`,
1 commit ahead of `origin/main`. PRD draft exists at
`docs/pr/rate-limit-login.md`.

# Acceptance

- The plan pushes the branch first (no force-push).
- PR title follows Conventional Commits.
- PR body sources from the existing PR draft, not a free-form summary.
- Reviewers are tagged by team where possible.
- The MCP tool `create_pull_request` (or `gh pr create`) is named explicitly.
