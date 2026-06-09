---
name: open-pr
description: Open a GitHub PR via the github MCP server — push current branch, draft from polymath-release:pr template, set base, add reviewers, never force-push.
---

# open-pr

> Open a real GitHub PR using the github MCP server. Pairs with `polymath-release:pr` (which drafts the description) and `polymath-release:changelog` (which updates CHANGELOG).

## When to use

- The user says "open a PR" or "ship this".
- A workflow finishes a code change and the next step is opening a PR.

## Inputs

- Current branch (must be ahead of `origin/<base>`).
- Optional: target base branch (default `main`).
- Optional: reviewer handles.
- Optional: `docs/pr/<slug>.md` from `polymath-release:pr`.

## Procedure

1. **Sanity checks** before pushing:
   - `git status` clean (no uncommitted changes that aren't intended to ship).
   - No secrets in the diff (the `polymath-engineering` secret-scan hook is a backstop, not a replacement for the check).
   - Branch tracks an upstream; if not, set it on push.
2. **Push** the branch:

   ```bash
   git push -u origin <branch>
   ```

   Never `--force` or `--force-with-lease` unless the user explicitly asked. If the push is rejected for non-fast-forward, stop and surface the conflict rather than overwriting upstream.
3. **Draft body** — if `docs/pr/<slug>.md` exists (from `polymath-release:pr`), use it. Otherwise compose a body following the canonical PR template.
4. **Create PR** via the github MCP tool `create_pull_request`:
   - `title`: Conventional Commits headline (`type(scope): summary`).
   - `body`: from step 3.
   - `base`: target base (default `main`).
   - `head`: current branch.
   - `draft`: `true` if the change isn't ready for review (build still red, etc.).
5. **Reviewers** — add via `request_reviewers` after creation. Tag by team if you can infer it from CODEOWNERS; otherwise ask the user.
6. **Return** the PR URL.

## Quality bar

- One commit per logical change — squash before pushing if the branch has fixup commits.
- PR title matches Conventional Commits.
- PR body is the structured template, not a free-form paragraph.
- Reviewers are tagged by team where possible.
- No force-push.

## Anti-patterns to avoid

- `git push --force` to "fix" a rejected push.
- Opening a PR against the wrong base because `origin/HEAD` was stale.
- Skipping `docs/pr/<slug>.md` when `polymath-release:pr` already drafted it.
