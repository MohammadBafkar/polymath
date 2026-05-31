#!/usr/bin/env bash
# Scaffold a new flows-lite workflow YAML from the canonical template.
#
# Usage: tools/new-workflow.sh <workflow-name> [target-plugin]
#   target-plugin defaults to "polymath-flows"
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <workflow-name> [target-plugin]" >&2
  exit 1
fi

name="$1"
plugin="${2:-polymath-flows}"

root="$(cd "$(dirname "$0")/.." && pwd)"
template="$root/tools/scaffolder-templates/Workflow.yaml"
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

# Rebuild the workflow routing index so the new workflow becomes discoverable and
# the WORKFLOW-INDEX conformance diff-guard stays green. The stub's placeholder
# triggers are not unique — fill in whenToUse/triggers, then re-run the builder.
if [[ "$plugin" == "polymath-flows" ]]; then
  python3 "$root/tools/build-workflow-index.py" >/dev/null 2>&1 \
    && echo "Rebuilt workflow index (edit whenToUse/triggers, then re-run tools/build-workflow-index.py)." \
    || echo "Note: fill in whenToUse/triggers, then run tools/build-workflow-index.py."
fi
