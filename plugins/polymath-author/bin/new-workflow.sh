#!/usr/bin/env bash
# Scaffold a new flows-lite workflow YAML from the canonical template.
#
# Usage: /polymath-author:new-workflow <workflow-name> [target-plugin]  (bin/new-workflow.sh)
#   target-plugin defaults to "polymath-flows"
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <workflow-name> [target-plugin]" >&2
  exit 1
fi

name="$1"
plugin="${2:-polymath-flows}"

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
# Prefer the plugin-bundled template (vendored copy) so the script works
# when installed standalone; fall back to the repo-root path for the
# legacy in-tree invocation.
template="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}/templates/Workflow.yaml"
[[ -f "$template" ]] || template="$root/tools/scaffolder-templates/Workflow.yaml"
target="$root/plugins/$plugin/workflows/$name.yaml"

if [[ ! -f "$template" ]]; then
  echo "error: workflow template not found at $template" >&2
  exit 1
fi
if [[ -f "$target" ]]; then
  echo "error: $target already exists" >&2
  exit 1
fi

mkdir -p "$(dirname "$target")"
sed -e "s/{{name}}/$name/g" -e "s/{{one_line_description}}/Replace this description./g" "$template" > "$target"
echo "Scaffolded $target"
