"""Tests for route-hint's opt-in adoption telemetry (POLYMATH_TELEMETRY=1).

The privacy contract: nothing is written without the exact opt-in value,
and the payload is surface names + timestamp only — never prompt text.

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
HOOK = REPO_ROOT / "plugins" / "polymath-core" / "hooks" / "scripts" / "route-hint.py"
FIRING_PROMPT = "Review this PR https://github.com/acme/web/pull/42 please"


def run_hook(pdata: pathlib.Path, telemetry: str | None) -> str:
    env = {k: v for k, v in os.environ.items()
           if k not in ("POLYMATH_ROUTE_MUTE", "POLYMATH_TELEMETRY")}
    env["CLAUDE_PLUGIN_DATA"] = str(pdata)
    if telemetry is not None:
        env["POLYMATH_TELEMETRY"] = telemetry
    with tempfile.TemporaryDirectory(prefix="hint-telemetry-") as scratch:
        (pathlib.Path(scratch) / ".git").mkdir()
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps({"prompt": FIRING_PROMPT}),
            capture_output=True,
            text=True,
            timeout=15,
            cwd=scratch,
            env=env,
        )
    return proc.stdout


class HintTelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.pdata = pathlib.Path(self._tmp.name)
        self.log = self.pdata / "polymath-core" / "hint-log.jsonl"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_off_by_default_writes_nothing(self) -> None:
        out = run_hook(self.pdata, telemetry=None)
        self.assertIn("[polymath-core route]", out)  # the hint itself fired
        self.assertFalse(self.log.exists())

    def test_zero_is_not_opt_in(self) -> None:
        run_hook(self.pdata, telemetry="0")
        self.assertFalse(self.log.exists())

    def test_opt_in_logs_surface_names_only(self) -> None:
        run_hook(self.pdata, telemetry="1")
        self.assertTrue(self.log.exists())
        doc = json.loads(self.log.read_text().splitlines()[0])
        self.assertIn("ts", doc)
        self.assertTrue(any("reviewPR" in s for s in doc["surfaces"]))
        # never prompt text
        self.assertNotIn("acme", self.log.read_text())


if __name__ == "__main__":
    unittest.main()
