#!/usr/bin/env bash
# polymath-core PostToolUse hook — event-time trigger.
#
# Thin wrapper around event-trigger.py. Degrades quiet when python3 is absent
# (the .py owns all logic, suppression, and its own error swallowing). A nudge
# must never block or break a turn, so this always exits 0.
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

python3 "${script_dir}/event-trigger.py" || true
exit 0
