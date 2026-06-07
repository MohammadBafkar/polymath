#!/usr/bin/env python3
"""polymath-core PostToolUse event-time trigger.

The highest-signal moment for routing is often *what just happened in the
session*, not the prompt text. This hook reads a Claude Code PostToolUse payload
on stdin and — only on a HIGH-PRECISION combination of signals — prints one quiet
line proposing the Polymath surface that fits the situation. It is the general,
data-driven version of the per-connector end-of-turn nudges (github suggest-pr,
snyk check-criticals): those remain as connector-specific instances of this same
pattern.

Design contract (mirrors route-hint.py):
* Detect -> propose. NEVER auto-runs anything.
* High precision over recall: a rule fires only when ALL of its required signals
  are present (e.g. a test *command* AND a failure marker in the output), so a
  passing run or an unrelated command stays silent.
* Quiet by default; suppressible via POLYMATH_ROUTE_MUTE / .polymath/route-muted.
* Degrade quiet: any error -> exit 0, no output. A nudge must never break a turn.

v1 ships one rule (failed test run -> bugTriage). The RULES table is the
extension point; add a rule, not a new hook.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Each rule: all `require` patterns must match the payload haystack to fire.
RULES = [
    {
        "id": "failed-tests",
        # The runner must appear in the COMMAND, and a failure marker in the OUTPUT
        # (matched separately so a benign command that merely names a runner, or a
        # passing run whose output mentions "failed" elsewhere, does not fire).
        "command": r"\b(pytest|go test|cargo test|jest|vitest|npm (run )?test|yarn test|dotnet test|mvn test|gradle test|rspec|phpunit|unittest)\b",
        "output": r"(=+ ?\d+ failed|--- FAIL|\bFAILED\b|Tests?:[^\n]*\bfailed\b|Failed!|Failures:\s*[1-9]|\b[1-9]\d* failed\b|\b[1-9]\d* failures?\b)",
        "surface": "polymath-flows:run-workflow bugTriage",
        "why": "test failures after a test run",
        "note": "root-cause the failure and plan the fix",
    },
]


def muted() -> bool:
    if os.environ.get("POLYMATH_ROUTE_MUTE"):
        return True
    here = Path.cwd()
    for d in (here, *here.parents):
        if (d / ".polymath" / "route-muted").exists():
            return True
        if (d / ".git").exists():
            break
    return False


def main() -> int:
    if muted():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    # Match the runner against the COMMAND and the failure marker against the
    # OUTPUT separately, so the failure signal must come from real test output —
    # not from the command text merely naming a runner. tool_response shape varies
    # (str or {stdout,stderr,...}); json.dumps captures it either way.
    tool_input = payload.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    output = json.dumps(payload.get("tool_response", ""), ensure_ascii=False)

    for rule in RULES:
        if re.search(rule["command"], command, re.IGNORECASE) and re.search(rule["output"], output, re.IGNORECASE):
            print(f"[polymath-core event] Detected {rule['why']}.")
            print(f"Consider: /{rule['surface']}  ({rule['note']})")
            print("Detect-only; nothing was run. Silence: POLYMATH_ROUTE_MUTE=1.")
            return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
