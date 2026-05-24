#!/usr/bin/env bash
# Materialize templates from shared/templates/ into each plugin that declares
# template usage. A plugin opts in by listing template file names in
# .claude-plugin/templates.json:
#
#   ["PRD.md", "User-story-map.md"]
#
# Materialization copies the files into plugins/<plugin>/templates/. This avoids
# cross-plugin symlinks (per § 7 of PLAN.md).
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
shared="$root/shared/templates"
plugins_dir="$root/plugins"
fail=0

for plugin in "$plugins_dir"/*/; do
  manifest="$plugin/.claude-plugin/templates.json"
  if [[ ! -f "$manifest" ]]; then
    continue
  fi
  dest="$plugin/templates"
  mkdir -p "$dest"
  while IFS= read -r tmpl; do
    [[ -z "$tmpl" ]] && continue
    src="$shared/$tmpl"
    if [[ ! -f "$src" ]]; then
      echo "✗ $(basename "$plugin"): missing template $tmpl in shared/templates/"
      fail=1
      continue
    fi
    cp "$src" "$dest/$tmpl"
    echo "✓ $(basename "$plugin"): materialized $tmpl"
  done < <(python3 -c "import json,sys;print('\n'.join(json.load(open(sys.argv[1]))))" "$manifest")
done

if [[ "$fail" -ne 0 ]]; then
  echo "link-templates: FAILED"
  exit 1
fi
echo "link-templates: OK"
