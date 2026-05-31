#!/usr/bin/env bash
# polymath-flows SessionStart hook — surface the workflow routing index.
#
# Workflows are otherwise invisible to the model: their YAML never reaches
# context, so the agent cannot propose a workflow it was not told to run. This
# injects the compact `name: whenToUse` list built by
# tools/build-workflow-index.py into data/workflow-index.min.json, so the agent
# can DETECT a matching workflow and PROPOSE it before running (the contract is
# documented in skills/run-workflow/SKILL.md). The header/footer text is kept
# byte-identical to the builder so its token assertion measures what is shown.
#
# Quiet by default: prints nothing if the index is missing, empty, muted, or
# python3 is unavailable. Suppress per-machine with:
#   touch "${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}/polymath-flows/index-muted"
set -euo pipefail

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
index="${root}/data/workflow-index.min.json"
data_root="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}"
mute_marker="${data_root}/polymath-flows/index-muted"

[[ -f "$mute_marker" ]] && exit 0
[[ -s "$index" ]] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

lines="$(python3 - "$index" <<'PY' 2>/dev/null || true
import json, sys
try:
    idx = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
if not isinstance(idx, list) or not idx:
    sys.exit(0)
print("Polymath workflows available (multi-step arcs you can run):")
for w in idx:
    print(f"  - {w['n']}: {w['w']}")
print(
    "Before starting substantial multi-step work that matches one of these, first "
    "propose that workflow in one line (name in backticks) and wait for approval; "
    "otherwise just answer. Never start a workflow without asking."
)
PY
)"

[[ -n "$lines" ]] && printf '%s\n' "$lines"
exit 0
