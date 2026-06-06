#!/usr/bin/env bash
# polymath-core UserPromptSubmit hook — ambient routing hint.
#
# Thin wrapper around route-hint.py. Degrades quiet when python3 is absent
# (the .py owns all logic, suppression, and its own error swallowing). A
# routing hint must never block or break a turn, so this always exits 0.
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

python3 "${script_dir}/route-hint.py" || true
exit 0
