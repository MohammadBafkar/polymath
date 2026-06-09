#!/usr/bin/env bash
# polymath-vcs Stop hook (GitHub Actions diagnostics)
#
# At end-of-turn, if the user has the GitHub CLI (`gh`) installed and the
# current repo's HEAD commit has a recently-failed Actions run, emit a single-
# line hint suggesting investigation or re-run via the github MCP server.
#
# Quiet by default. Skips silently when gh is missing, the repo is not on
# GitHub, or the latest run is queued/in-progress/success.
set -euo pipefail

# Need gh + a git repo.
command -v gh >/dev/null 2>&1 || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# Only react when authenticated; never prompt mid-session.
gh auth status >/dev/null 2>&1 || exit 0

# Latest run on the current branch.
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
[[ -z "$branch" || "$branch" == "HEAD" ]] && exit 0

run_json="$(gh run list --branch "$branch" --limit 1 --json status,conclusion,name,url 2>/dev/null || echo '[]')"
[[ "$run_json" == "[]" || -z "$run_json" ]] && exit 0

read -r status conclusion name url <<<"$(printf '%s' "$run_json" | python3 -c '
import json, sys
try:
    rows = json.load(sys.stdin)
    if not rows: sys.exit(0)
    r = rows[0]
    print(r.get("status",""), r.get("conclusion",""), r.get("name",""), r.get("url",""))
except Exception:
    pass
')"

[[ "$status" != "completed" ]] && exit 0
case "$conclusion" in
  failure|cancelled|timed_out)
    echo "[polymath-vcs] Latest CI run \"$name\" on \`$branch\` ended in $conclusion. $url — fetch logs via the github MCP server or re-run with workflow.dispatch?"
    ;;
esac

exit 0
