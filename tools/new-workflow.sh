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
template="$root/shared/templates/Workflow.yaml"
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
