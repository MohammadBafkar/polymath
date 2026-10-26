"""Tests for the planning skills' deterministic calculators:
estimate/scripts/pert.py, forecast/scripts/monte-carlo.py, prioritize/scripts/score.py.

Run with: python3 -m unittest discover -s plugins/polymath-planning/tests
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

SKILLS = pathlib.Path(__file__).resolve().parents[1] / "skills"
PERT = SKILLS / "estimate" / "scripts" / "pert.py"
MONTE = SKILLS / "forecast" / "scripts" / "monte-carlo.py"
SCORE = SKILLS / "prioritize" / "scripts" / "score.py"


def run(script: pathlib.Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], input=stdin,
                          capture_output=True, text=True, timeout=60)


class PertTest(unittest.TestCase):
    CSV = "step,o,e,p,critical\nmigrate,2,4,8,y\nlimiter,1,2,8,y\nrunbook,1,1,2,n\n"

    def test_step_math_and_totals(self):
        r = run(PERT, "--focus-hours", "5", stdin=self.CSV)
        self.assertEqual(r.returncode, 0, r.stderr)
        # (2 + 16 + 8) / 6 = 4.33, (8 - 2) / 2.56 = 2.34
        self.assertRegex(r.stdout, r"1\. migrate\s+2\s+4\s+8\s+4\.3\s+2\.3")
        # critical path only: 4.33 + 2.83; sigma = sqrt(2.34^2 + 2.73^2) = 3.6
        self.assertIn("Critical path mean: 7.2 h ≈ 1.4 working days", r.stdout)
        self.assertIn("80% interval: 2.6 .. 11.8 h", r.stdout)
        self.assertIn("σ_total = 3.6 h", r.stdout)

    def test_flags(self):
        out = run(PERT, stdin=self.CSV).stdout
        self.assertIn("migrate", out.split("Decompose before committing:")[1])  # P/O = 4
        self.assertNotIn("runbook", out.split("Decompose before committing:")[1])  # P/O = 2
        self.assertIn("off critical path", out)

    def test_rejects_out_of_order_points(self):
        r = run(PERT, stdin="step,o,e,p\nx,5,3,8\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("O <= E <= P", r.stderr)

    def test_rejects_missing_columns(self):
        self.assertEqual(run(PERT, stdin="step,o,e\nx,1,2\n").returncode, 2)

    def test_deterministic(self):
        self.assertEqual(run(PERT, stdin=self.CSV).stdout, run(PERT, stdin=self.CSV).stdout)

    def test_draft_numbers_are_marked(self):
        out = run(PERT, stdin="step,o,e,p\nx,2?,4?,6?\ny,1,2,3\n").stdout
        self.assertIn("DRAFT — numbers not confirmed by the team", out.splitlines()[0])
        self.assertIn("Drafted numbers: 1 of 2 steps", out)
        self.assertRegex(out, r"1\. x .*draft")
        self.assertNotIn("DRAFT", run(PERT, stdin=self.CSV).stdout)


class MonteCarloTest(unittest.TestCase):
    def test_constant_throughput_is_exact(self):
        r = run(MONTE, "--throughput", "4,4,4,4,4,4", "--items", "40")
        self.assertEqual(r.returncode, 0, r.stderr)
        for lv in (50, 70, 85, 95):
            self.assertRegex(r.stdout, rf"P{lv}\s+done within 10 weeks")
        r = run(MONTE, "--throughput", "4,4,4,4,4,4", "--periods", "5")
        self.assertRegex(r.stdout, r"P85\s+at least 20 items")

    def test_same_seed_same_output_and_seed_matters(self):
        args = ("--throughput", "3,5,2,4,6,0,4,5", "--items", "40")
        a, b = run(MONTE, *args).stdout, run(MONTE, *args).stdout
        self.assertEqual(a, b)
        self.assertIn("seed 42", a)

    def test_percentiles_are_monotonic(self):
        out = run(MONTE, "--throughput", "3,5,2,4,6,0,4,5", "--items", "40").stdout
        weeks = [int(w) for w in __import__("re").findall(r"done within (\d+) weeks", out)]
        self.assertEqual(weeks, sorted(weeks))
        items = [int(w) for w in __import__("re").findall(
            r"at least (\d+) items", run(MONTE, "--throughput", "3,5,2,4,6,0,4,5", "--periods", "10").stdout)]
        self.assertEqual(items, sorted(items, reverse=True))

    def test_sparse_history_warns_and_zero_history_fails(self):
        self.assertIn("WARNING: only 3 weeks", run(MONTE, "--throughput", "1,0,2", "--items", "5").stdout)
        self.assertEqual(run(MONTE, "--throughput", "0,0,0", "--items", "5").returncode, 2)


class ScoreTest(unittest.TestCase):
    RICE = ("item,reach,impact,confidence,effort\n"
            "SSO login,2000?,2,80,4\nBulk refunds,500,3,50,2\n"
            "Dark mode,4000,0.5,100,2\nCSV export,1000,1,100,1\n")

    def rows(self, out: str) -> list[list[str]]:
        return [[c.strip() for c in line.strip("|").split("|")]
                for line in out.splitlines() if line.startswith("| ") and not line.startswith("| Rank")]

    def test_rice_order_and_tie_break(self):
        r = run(SCORE, "--method", "rice", stdin=self.RICE)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = self.rows(r.stdout)
        self.assertEqual([row[1] for row in rows], ["CSV export", "Dark mode", "SSO login", "Bulk refunds"])
        # CSV export and Dark mode both score 1,000 at 100% confidence: lower effort wins.
        self.assertEqual(rows[1][0], "2=")
        self.assertEqual(rows[2][2], "2,000?")  # guess marker carried into the table

    def test_flags_low_confidence_and_guess_sensitivity(self):
        out = run(SCORE, "--method", "rice", stdin=self.RICE).stdout
        self.assertIn("LOW CONFIDENCE (50%): Bulk refunds", out)
        self.assertIn("SSO login: guessed reach; rank moves 1–3", out)

    def test_wsjf(self):
        csv = ("item,value,time_criticality,risk_reduction,job_size\n"
               "A,8,5,2,5\nB,5,8,2,5\nC,3,1,1,1\n")
        rows = self.rows(run(SCORE, "--method", "wsjf", stdin=csv).stdout)
        self.assertEqual([r[1] for r in rows], ["C", "A", "B"])
        self.assertEqual(rows[0][-2:], ["5", "5"])  # cost of delay 5, wsjf 5
        self.assertEqual(rows[2][0], "3=")  # A and B tie on everything: input order

    def test_rejects_bad_inputs(self):
        bad_impact = "item,reach,impact,confidence,effort\nx,10,4,50,1\n"
        self.assertEqual(run(SCORE, "--method", "rice", stdin=bad_impact).returncode, 2)
        blank = "item,reach,impact,confidence,effort\nx,,1,50,1\n"
        r = run(SCORE, "--method", "rice", stdin=blank)
        self.assertEqual(r.returncode, 2)
        self.assertIn("never leave it blank", r.stderr)


if __name__ == "__main__":
    unittest.main()
