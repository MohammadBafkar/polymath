#!/usr/bin/env bash
# polymath-vcs Stop hook
#
# At end-of-turn, when the working tree has uncommitted edits to source files,
# nudge the user toward opening a PR — but only quietly, and only when there
# are committed-but-unpushed commits or staged changes that warrant it.
#
# Quiet by default. Never blocks (exit 0). Prints at most one line.
set -euo pipefail

cwd="$(pwd)"

# Only emit if cwd is a git repo.
if ! git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Are there committed-but-unpushed commits on the current branch?
upstream="$(git -C "$cwd" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
if [[ -n "$upstream" ]]; then
  ahead="$(git -C "$cwd" rev-list --count "$upstream"..HEAD 2>/dev/null || echo 0)"
  if [[ "$ahead" -gt 0 ]]; then
    branch="$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
    echo "[polymath-vcs] $ahead unpushed commit(s) on \`$branch\`. Ready to push and open a PR via the github MCP server?"
    exit 0
  fi
fi

# Otherwise stay silent.
exit 0
