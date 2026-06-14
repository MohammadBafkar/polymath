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
# caller's marketplace). Fall back to $POLYMATH_PROJECT_DIR, then the legacy
# $CLAUDE_PROJECT_DIR, then to $PWD.
find_marketplace_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/.claude-plugin/marketplace.json" ]]; then
      printf '%s' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  if [[ -n "${POLYMATH_PROJECT_DIR:-}" && -f "${POLYMATH_PROJECT_DIR}/.claude-plugin/marketplace.json" ]]; then
    printf '%s' "$POLYMATH_PROJECT_DIR"
    return 0
  fi
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

Show the exact shape the skill produces (the model imitates this):

\`\`\`text
<output skeleton — replace with the concrete files, frontmatter, or fields>
\`\`\`

## References

- [plugin templates](../../templates/) — reference the plugin's own templates/ dir.
MD

echo "Scaffolded $skill_dir"

# Register the skill's routing posture. Knowledge skills default to
# a routing exemption so a fresh scaffold passes conformance; replace it with a
# skills/<skill>/routing.yaml if the skill has a deterministic prompt signal.
exemptions="$root/registry/routing-exemptions.json"
surface="$plugin:$skill"
if [[ -f "$exemptions" ]] && command -v python3 >/dev/null 2>&1; then
  if python3 - "$exemptions" "$surface" <<'PY'; then
import json, sys
path, surface = sys.argv[1], sys.argv[2]
data = json.load(open(path))
ex = data.setdefault("exemptions", {})
if surface in ex:
    raise SystemExit(1)  # already present — nothing to do
ex[surface] = ("knowledge/procedure surface routed by its description; no "
               "deterministic prompt signal declared yet — declare routing.yaml "
               "or keep this entry")
data["exemptions"] = dict(sorted(ex.items()))
open(path, "w").write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
    echo "Registered routing exemption for $surface."
  fi
fi

echo
echo "Next steps:"
echo "  1. Flesh out $skill_dir/SKILL.md (description, procedure, output shape)."
echo "  2. Add \`$skill\` to the 'Skills:' list in plugins/$plugin/README.md (DOCS-2)."
echo "  3. Run: tools/conformance.sh $plugin"
