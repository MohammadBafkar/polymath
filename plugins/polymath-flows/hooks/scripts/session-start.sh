#!/usr/bin/env bash
# polymath-flows SessionStart hook — surface the workflow routing index.
#
# Workflows are otherwise invisible to the model: their YAML never reaches
# context, so the agent cannot propose a workflow it was not told to run. This
# delegates to hooks/scripts/project-index.py, which injects the TIERED
# `name: whenToUse` list built by tools/build-workflow-index.py: Tier A
# (repo-relevant workflows first — detectionSignals paths probed against the
# repo — alphabetical fill, ≤400-token block), a one-line Tier B pointer for
# the rest, and a machine-local fragment for project-/user-layer workflows
# (written to ${CLAUDE_PLUGIN_DATA}/polymath-flows/workflow-index.project.json
# together with the tiering record doctor renders). The propose/confirm
# contract is documented in skills/run-workflow/SKILL.md.
#
# Quiet by default: prints nothing if there is nothing to index, the index is
# muted, or python3 is unavailable. Suppress per-machine with:
#   touch "${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}/polymath-flows/index-muted"
set -euo pipefail

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
min_index="${root}/data/workflow-index.min.json"
full_index="${root}/data/workflow-index.json"
detect_index="${root}/data/workflow-detect.json"
data_root="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}"
mute_marker="${data_root}/polymath-flows/index-muted"

[[ -f "$mute_marker" ]] && exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 "${root}/hooks/scripts/project-index.py" "$min_index" "$full_index" "$data_root" "$detect_index" 2>/dev/null || true
exit 0
