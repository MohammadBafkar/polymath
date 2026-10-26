"""Tests for eval-plan/scripts/winrate.py — pairwise ship verdicts.

Run with: python3 -m unittest discover -s plugins/polymath-ai/tests
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "eval-plan" / "scripts" / "winrate.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30)


class WinrateTest(unittest.TestCase):
    def test_threshold_example_from_the_skill(self):
        out = run("--wins", "114", "--losses", "86").stdout
        self.assertIn("Verdict: SHIP", out)
        self.assertIn("Wins needed to ship at n = 200: 114", out)
        self.assertIn("NOT DISTINGUISHABLE", run("--wins", "110", "--losses", "90").stdout)  # 55% at N = 200

    def test_regression_and_ties(self):
        out = run("--wins", "60", "--losses", "140", "--ties", "30").stdout
        self.assertIn("REGRESSION", out)
        self.assertIn("/ 30 ties (ties excluded)", out)
        self.assertIn("of 200 decisive comparisons", out)

    def test_validation(self):
        self.assertEqual(run("--wins", "0", "--losses", "0").returncode, 2)
        self.assertEqual(run("--wins", "-1", "--losses", "3").returncode, 2)


if __name__ == "__main__":
    unittest.main()
