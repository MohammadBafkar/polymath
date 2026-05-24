#!/usr/bin/env bash
# polymath-connector-github UserPromptSubmit hook
#
# When the user's prompt contains a GitHub PR URL, print a hint to stdout
# routing the model toward the github MCP server's PR-fetch tool. This is a
# hint, not a block — exits 0 with stdout context.
#
# Reads the prompt payload from stdin.
set -euo pipefail

payload="$(cat)"

prompt="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("prompt", ""))
except Exception:
    pass
' 2>/dev/null || true)"

[[ -z "$prompt" ]] && exit 0

# Match PR URLs of the shape https://github.com/<owner>/<repo>/pull/<number>
match="$(printf '%s' "$prompt" | grep -oE 'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/[0-9]+' | head -1 || true)"
[[ -z "$match" ]] && exit 0

owner_repo_pr="$(printf '%s' "$match" | sed -E 's|https://github.com/([^/]+/[^/]+)/pull/([0-9]+)|\1#\2|')"

cat <<EOF
[polymath-connector-github] PR URL detected: $match
Hint to assistant: fetch the PR ($owner_repo_pr) and its diff via the
\`github\` MCP server before responding. Useful tools on that server:
  - get_pull_request           (number, owner, repo)
  - get_pull_request_files     (diff metadata)
  - list_pull_request_reviews  (existing review state)
EOF
