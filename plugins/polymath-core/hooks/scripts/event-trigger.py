#!/usr/bin/env python3
"""polymath-core PostToolUse event-time trigger.

The highest-signal moment for routing is often *what just happened in the
session*, not the prompt text. This hook reads a Claude Code PostToolUse payload
on stdin and — only on a HIGH-PRECISION combination of signals — prints one quiet
line proposing the Polymath surface that fits the situation. It is the general,
data-driven version of the per-connector end-of-turn nudges (github suggest-pr,
snyk check-criticals): those remain as connector-specific instances of this same
pattern.

Rules are DATA, not code: each routable surface declares its event triggers in
its routing.yaml sidecar (`events:` — see
registry/schemas/surface-routing.schema.json); tools/build-surface-index.py
compiles them into the `events` list of data/route-signals.json, which this
hook reads. Add a rule by editing the surface's sidecar and rebuilding — never
by editing this file.

Design contract (mirrors route-hint.py):
* Detect -> propose. NEVER auto-runs anything.
* High precision over recall: a rule fires only when ALL of its required signals
  are present (the `command` regex against the tool command AND the `output`
  regex against the tool output), so a passing run or an unrelated command
  stays silent.
* Quiet by default; suppressible via POLYMATH_ROUTE_MUTE / .polymath/route-muted.
* Degrade quiet: any error -> exit 0, no output. A nudge must never break a turn.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


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


def load_events() -> list[dict]:
    table = Path(__file__).resolve().parent.parent.parent / "data" / "route-signals.json"
    try:
        doc = json.loads(table.read_text())
    except Exception:
        return []
    events = doc.get("events", [])
    if not isinstance(events, list):
        return []
    return [e for e in events if isinstance(e, dict)]


def main() -> int:
    if muted():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    rules = load_events()
    if not rules:
        return 0
    # Match the trigger against the COMMAND and the marker against the OUTPUT
    # separately, so the output signal must come from real tool output — not
    # from the command text merely naming a runner. tool_response shape varies
    # (str or {stdout,stderr,...}); json.dumps captures it either way.
    tool_input = payload.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    output = json.dumps(payload.get("tool_response", ""), ensure_ascii=False)

    for rule in rules:
        try:
            cmd_rx = re.compile(str(rule.get("command") or ""), re.IGNORECASE)
            out_rx = re.compile(str(rule.get("output") or ""), re.IGNORECASE)
        except re.error:
            continue  # a bad compiled pattern must not take down the hook
        if not rule.get("surface") or not rule.get("why"):
            continue
        if cmd_rx.search(command) and out_rx.search(output):
            note = rule.get("note") or "see the proposed surface"
            print(f"[polymath-core event] Detected {rule['why']}.")
            print(f"Consider: /{rule['surface']}  ({note})")
            print("Detect-only; nothing was run. Silence: POLYMATH_ROUTE_MUTE=1.")
            return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
