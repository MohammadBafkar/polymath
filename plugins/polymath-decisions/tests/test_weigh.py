"""Tests for tradeoff-matrix/scripts/weigh.py — weighted totals and the ±1
sensitivity sweep.

Run with: python3 -m unittest discover -s plugins/polymath-decisions/tests
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

WEIGH = pathlib.Path(__file__).resolve().parents[1] / "skills" / "tradeoff-matrix" / "scripts" / "weigh.py"

TEMPLATE = (
    "criterion,weight,A. In-memory,B. Redis,C. Postgres\n"
    "Latency (P99),5,5,5,3\n"
    "Operational burden,4,5,3,4\n"
    "Cost (monthly),3,5,4,3\n"
    "Time to ship,3,5,4,4\n"
    "Cross-team buy-in,2,5,4,5\n"
)
CLOSE = "criterion,weight,Redis,Postgres\nLatency,5,4?,3\nDurability,3,3,5\nFamiliarity,2,4,4\n"


def run(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(WEIGH)], input=stdin, capture_output=True, text=True, timeout=30)


class WeighTest(unittest.TestCase):
    def test_template_totals_and_cell_math(self):
        r = run(TEMPLATE)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("| A. In-memory | 5 × 5 = 25 | 5 × 4 = 20 | 5 × 3 = 15 | 5 × 3 = 15 | 5 × 2 = 10 | **85** |", r.stdout)
        self.assertIn("2. B. Redis — 69", r.stdout)
        self.assertIn("3. C. Postgres — 62", r.stdout)
        self.assertIn("No single ±1 change flips the winner.", r.stdout)

    def test_close_call_lists_every_hinge(self):
        out = run(CLOSE).stdout
        self.assertIn("1. Postgres — 38", out)
        self.assertIn("- Redis on Latency 4→5 (GUESSED score): Redis wins", out)
        self.assertIn("- weight of Durability 3→2: Redis wins", out)
        self.assertIn("The decision hinges on: Latency, Durability, Familiarity", out)
        self.assertIn("1 guessed score(s)", out)

    def test_non_differentiating_criterion(self):
        out = run(CLOSE).stdout
        section = out.split("Non-differentiating criteria")[1].split("Sensitivity")[0]
        self.assertIn("- Familiarity", section)
        self.assertNotIn("Latency", section)

    def test_top_tie_is_not_a_winner(self):
        out = run("criterion,weight,X,Y\nSpeed,3,4,4\nCost,2,2,2\n").stdout
        self.assertIn("No sole winner", out)

    def test_validation(self):
        self.assertEqual(run("criterion,weight,X,Y\nSpeed,3,6,4\nCost,2,2,2\n").returncode, 2)  # score > 5
        self.assertEqual(run("criterion,weight,X,Y\nSpeed,3?,4,4\nCost,2,2,2\n").returncode, 2)  # guessed weight
        self.assertEqual(run("crit,w,X,Y\nSpeed,3,4,4\nCost,2,2,2\n").returncode, 2)  # bad header
        self.assertEqual(run("criterion,weight,X\nSpeed,3,4\nCost,2,2\n").returncode, 2)  # one option

    def test_deterministic(self):
        self.assertEqual(run(CLOSE).stdout, run(CLOSE).stdout)


if __name__ == "__main__":
    unittest.main()
