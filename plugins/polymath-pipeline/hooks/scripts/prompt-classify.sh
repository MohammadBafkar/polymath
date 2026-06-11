#!/usr/bin/env bash
# polymath-pipeline UserPromptSubmit — emit the classify directive (once per
# unclassified hour) and stamp the session marker. Silent when routing.mode
# is hint/absent; fail-open without python3. Never blocks a prompt.
set -uo pipefail
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
command -v python3 >/dev/null 2>&1 || exit 0
python3 "${root}/bin/polymath-pipeline" hook-prompt 2>/dev/null || true
exit 0
