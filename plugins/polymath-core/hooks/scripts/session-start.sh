#!/usr/bin/env bash
# polymath-core SessionStart hook
#
# Prints the active Polymath plugins, and any paused workflows from
# ${CLAUDE_PLUGIN_DATA}/workflows/.
#
# Quiet by default — only prints when there is something to surface.
set -euo pipefail

data_root="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}"
workflows="$data_root/workflows"

paused=()
if [[ -d "$workflows" ]]; then
  while IFS= read -r state; do
    status="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('status','unknown'))" "$state" 2>/dev/null || echo unknown)"
    if [[ "$status" == "paused" ]]; then
      paused+=("$(basename "$(dirname "$state")")")
    fi
  done < <(find "$workflows" -maxdepth 2 -name state.json 2>/dev/null)
fi

if [[ ${#paused[@]} -gt 0 ]]; then
  echo "Polymath: ${#paused[@]} paused workflow(s):"
  for w in "${paused[@]}"; do
    echo "  - $w  (resume with /polymath-flows:resume-workflow $w)"
  done
fi
