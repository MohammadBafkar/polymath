#!/usr/bin/env bash
# Scaffold a new skill inside a Polymath plugin.
#
# Usage: /polymath-author:new-skill <plugin-name> <skill-name> [description]  (bin/new-skill.sh)
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <plugin-name> <skill-name> [description]" >&2
  exit 1
fi

plugin="$1"
skill="$2"
description="${3:-Replace this description.}"

if [[ "$plugin" != polymath-* ]]; then
  plugin="polymath-$plugin"
fi

# Locate the *caller's* marketplace root, not this plugin's bin/.
# Walk up from $PWD looking for .claude-plugin/marketplace.json (the
# caller's marketplace). Fall back to $CLAUDE_PROJECT_DIR, then to $PWD.
find_marketplace_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/.claude-plugin/marketplace.json" ]]; then
      printf '%s' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  if [[ -n "${CLAUDE_PROJECT_DIR:-}" && -f "${CLAUDE_PROJECT_DIR}/.claude-plugin/marketplace.json" ]]; then
    printf '%s' "$CLAUDE_PROJECT_DIR"
    return 0
  fi
  printf '%s' "$PWD"
}
root="$(find_marketplace_root)"
skill_dir="$root/plugins/$plugin/skills/$skill"

if [[ ! -d "$root/plugins/$plugin" ]]; then
  echo "error: plugin $plugin does not exist; run /polymath-author:new-plugin first" >&2
  exit 1
fi
if [[ -d "$skill_dir" ]]; then
  echo "error: $skill_dir already exists" >&2
  exit 1
fi

mkdir -p "$skill_dir"

cat > "$skill_dir/SKILL.md" <<MD
---
name: $skill
description: $description
---

# $skill

> One-line restatement of when this skill should be used (≤ 200 chars).

## When to use

- Trigger 1
- Trigger 2

## Procedure

1. Step 1
2. Step 2
3. Step 3

## Output

What this skill is expected to produce. List concrete files, frontmatter, or summary fields.

## References

- [plugin templates](../../templates/) — reference the plugin's own templates/ dir.
MD

echo "Scaffolded $skill_dir"
