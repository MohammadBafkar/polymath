#!/usr/bin/env bash
# polymath-pipeline SessionStart — announce active classify/enforce mode and
# run the retention sweep. Silent (constant-time exit) when the repo does not
# declare routing.mode classify|enforce; fail-open without python3.
set -uo pipefail
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
command -v python3 >/dev/null 2>&1 || exit 0
python3 "${root}/bin/polymath-pipeline" hook-session-start 2>/dev/null || true
exit 0
