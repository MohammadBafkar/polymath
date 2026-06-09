# GitHub MCP tools (reference)

This connector ships an `.mcp.json` that runs `@modelcontextprotocol/server-github` via `npx`. The token is injected from `userConfig.githubToken` and exposed to the server as `GITHUB_PERSONAL_ACCESS_TOKEN`.

## Tools exposed (subject to upstream MCP version)

### Repositories

- `search_repositories` — find repos by query.
- `get_file_contents` — read a file at a path/ref.
- `list_commits` — list commits on a branch.
- `search_code` — code search across accessible repos.

### Pull requests

- `create_pull_request` — open a PR (title, body, head, base, draft).
- `get_pull_request` — fetch one PR.
- `get_pull_request_files` — diff metadata.
- `get_pull_request_reviews` — existing reviews.
- `list_pull_requests` — list with filters (state, head, base, sort).
- `create_pull_request_review` — submit a review (APPROVE / REQUEST_CHANGES / COMMENT).
- `merge_pull_request` — merge with the chosen method.
- `request_reviewers` — tag reviewers.

### Issues

- `create_issue` — open one.
- `get_issue` — read one.
- `add_issue_comment` — append a comment.
- `update_issue` — labels, assignees, state.
- `list_issues` — list with filters.
- `search_issues` — issue search query.

### Branches

- `create_branch`, `list_branches`.

## Token scopes

Fine-grained PAT recommended. For repo-only use:

- `contents: read+write`
- `pull_requests: read+write`
- `issues: read+write`
- `metadata: read`
- `workflows: read+write` (required by this plugin's `diagnose-ci-failure` skill and `check-recent-ci.sh` Stop hook)

For read-only triage workloads, drop the write scopes.

## Anti-patterns

- Granting `admin:*` on the PAT.
- Sharing the same long-lived classic PAT across services.
- Storing the PAT in `.bashrc` — set it through `userConfig` so it's scoped to the plugin.
