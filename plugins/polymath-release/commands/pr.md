---
name: pr
description: Draft a PR description for the current branch following the canonical PR template; saves the draft to docs/pr/<slug>.md without opening a real PR.
---

# /pr

Thin alias for the `polymath-release:pr` skill — drafts the PR body
from current-branch commits + PRD context and writes to
`docs/pr/<slug>.md`. **Does not** open a real PR; pair with
`polymath-connector-github:open-pr` to push + open via MCP.
