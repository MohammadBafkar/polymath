---
name: pr
description: Slash entry point after committing — writes a PR body to docs/pr/<slug>.md; opens no real PR.
---

# /pr

Thin alias for the `polymath-release:pr` skill — drafts the PR body
from current-branch commits + PRD context and writes to
`docs/pr/<slug>.md`. **Does not** open a real PR; pair with
`polymath-vcs:open-pr` to push + open via MCP.
