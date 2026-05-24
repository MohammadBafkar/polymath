#!/usr/bin/env bash
# Scaffold a new skill inside a Polymath plugin.
#
# Usage: tools/new-skill.sh <plugin-name> <skill-name> [description]
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

root="$(cd "$(dirname "$0")/.." && pwd)"
skill_dir="$root/plugins/$plugin/skills/$skill"

if [[ ! -d "$root/plugins/$plugin" ]]; then
  echo "error: plugin $plugin does not exist; run tools/new-plugin.sh first" >&2
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

- [shared/templates/…](../../../../shared/templates/)
MD

echo "Scaffolded $skill_dir"
