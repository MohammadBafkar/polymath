"""Tests for hooks/scripts/event-trigger.py — the data-driven PostToolUse
nudge. Rules come from the compiled `events` list in data/route-signals.json
(declared in routing.yaml sidecars), not from code.

Run with: python3 -m unittest discover -s plugins/polymath-core/tests
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "plugins" / "polymath-core" / "hooks" / "scripts" / "event-trigger.py"


def run_hook(payload: dict) -> str:
    env = {k: v for k, v in os.environ.items() if k != "POLYMATH_ROUTE_MUTE"}
    with tempfile.TemporaryDirectory(prefix="event-trigger-") as scratch:
        (pathlib.Path(scratch) / ".git").mkdir()  # stop the mute-marker walk
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=15,
            cwd=scratch,
            env=env,
        )
    return proc.stdout


class EventTriggerTests(unittest.TestCase):
    def test_failing_test_run_proposes_bug_triage(self) -> None:
        out = run_hook({
            "tool_input": {"command": "pytest tests/"},
            "tool_response": "==== 3 failed, 7 passed in 1.2s ====",
        })
        self.assertIn("polymath-flows:run-workflow bugTriage", out)
        self.assertIn("Detect-only", out)

    def test_passing_run_is_silent(self) -> None:
        out = run_hook({
            "tool_input": {"command": "pytest tests/"},
            "tool_response": "==== 10 passed in 1.2s ====",
        })
        self.assertEqual(out, "")

    def test_failure_marker_in_command_alone_is_silent(self) -> None:
        # The output regex must match real OUTPUT — a command merely naming
        # a runner plus the word "failed" elsewhere must not fire.
        out = run_hook({
            "tool_input": {"command": "grep -rn failed docs/"},
            "tool_response": "docs/x.md: tests failed last week",
        })
        self.assertEqual(out, "")

    def test_malformed_payload_degrades_quiet(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "POLYMATH_ROUTE_MUTE"}
        with tempfile.TemporaryDirectory(prefix="event-trigger-") as scratch:
            (pathlib.Path(scratch) / ".git").mkdir()
            proc = subprocess.run(
                [sys.executable, str(HOOK)],
                input="this is not json",
                capture_output=True,
                text=True,
                timeout=15,
                cwd=scratch,
                env=env,
            )
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_rules_come_from_compiled_table(self) -> None:
        table = json.loads(
            (REPO_ROOT / "plugins" / "polymath-core" / "data" / "route-signals.json").read_text()
        )
        events = table.get("events") or []
        self.assertTrue(events, "compiled events list must not be empty")
        self.assertTrue(all(e.get("surface") and e.get("command") and e.get("output") for e in events))


if __name__ == "__main__":
    unittest.main()
