#!/usr/bin/env bash
# polymath-pipeline PreToolUse — the enforce gate. MUST propagate the
# engine's exit code: 2 = deny (stderr is shown to the model), 0 = allow.
# Anything unexpected fails open (exit 0); the engine audits its own
# fail-opens to the decision log.
set -uo pipefail
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
command -v python3 >/dev/null 2>&1 || exit 0
python3 "${root}/bin/polymath-pipeline" hook-pretool
code=$?
[[ "$code" -eq 2 ]] && exit 2
exit 0
