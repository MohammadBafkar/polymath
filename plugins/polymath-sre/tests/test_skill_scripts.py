"""Tests for the SRE skills' calculators: slo-design/scripts/error-budget.py
(the budget arithmetic slo-design and error-budget-policy quote) and
capacity-plan/scripts/headroom.py (growth fit + must-act-by date).

Run with: python3 -m unittest discover -s plugins/polymath-sre/tests
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "slo-design" / "scripts" / "error-budget.py"
HEADROOM = pathlib.Path(__file__).resolve().parents[1] / "skills" / "capacity-plan" / "scripts" / "headroom.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30)


class ErrorBudgetTest(unittest.TestCase):
    def test_28_day_budget_table(self):
        # The exact figures slo-design publishes for a 28-day window.
        expected = {
            "99.0": "6h 43m 12s",
            "99.5": "3h 21m 36s",
            "99.9": "40m 19s",
            "99.95": "20m 10s",
            "99.99": "4m 2s",
        }
        for slo, hms in expected.items():
            r = run("--slo", slo, "--window-days", "28")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(f"= {hms} per 28d", r.stdout, slo)

    def test_30_day_figures_differ(self):
        self.assertIn("= 43m 12s per 30d", run("--slo", "99.9", "--window-days", "30").stdout)

    def test_burn_rates(self):
        out28 = run("--slo", "99.5", "--window-days", "28").stdout
        for rate in ("13.44×", "5.60×", "0.93×"):
            self.assertIn(rate, out28)
        out30 = run("--slo", "99.5", "--window-days", "30").stdout
        for rate in ("14.40×", "6.00×", "1.00×"):
            self.assertIn(rate, out30)

    def test_states(self):
        def state(*extra):
            return run("--slo", "99.5", "--window-days", "28", *extra).stdout.split("State:")[1].split()[0]
        self.assertEqual(state("--consumed-minutes", "100"), "HEALTHY")  # 49.6%
        self.assertEqual(state("--consumed-minutes", "140"), "ERODING")  # 69.4%
        self.assertEqual(state("--consumed-minutes", "201.6"), "ERODING")  # exactly 100%
        self.assertEqual(state("--consumed-minutes", "202"), "EXHAUSTED")
        self.assertEqual(state("--requests", "2000000", "--failed", "10001"), "EXHAUSTED")
        self.assertEqual(state("--requests", "2000000", "--failed", "4000"), "HEALTHY")

    def test_validation(self):
        self.assertEqual(run("--slo", "100").returncode, 2)
        self.assertEqual(run("--slo", "abc").returncode, 2)
        self.assertEqual(run("--slo", "99.9", "--requests", "10").returncode, 2)  # --failed missing


def headroom(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HEADROOM), *args], capture_output=True, text=True, timeout=30)


class HeadroomTest(unittest.TestCase):
    BASE = ("--period", "month", "--capacity", "100", "--ceiling", "0.7", "--as-of", "2026-10-26")

    def test_fit_picks_higher_r2_and_projects_from_last_value(self):
        r = headroom("--history", "41,43,44,46,49,51", "--lead-time-days", "42", *self.BASE)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r"linear\s+\+2\.00/month\s+R² 0\.981")
        self.assertRegex(r.stdout, r"compound \+4\.46%/month\s+R² 0\.987   ← chosen \(higher R²\)")
        self.assertIn("Trend:     breach in 7.3 months → 2027-06-03", r.stdout)
        self.assertIn("Must act by: 2027-04-22 (first breach 2027-06-03, trend)", r.stdout)

    def test_event_breach_pulls_the_date_forward(self):
        out = headroom("--history", "41,43,44,46,49,51", "--lead-time-days", "42",
                       "--event", "2026-11-27:2.5", *self.BASE).stdout
        self.assertIn("2026-11-27 ×2.5 → projected 133.5  BREACH", out)
        self.assertIn("Must act by: 2026-10-16", out)
        self.assertIn("already past: act now", out)

    def test_stated_growth_and_flat_history(self):
        out = headroom("--current", "51", "--growth", "+2", "--lead-time-days", "30", *self.BASE).stdout
        self.assertIn("stated, not fitted", out)
        self.assertIn("breach in 9.5 months → 2027-08-11", out)
        flat = headroom("--history", "10,10,10", "--lead-time-days", "30", *self.BASE).stdout
        self.assertIn("R² tie → compound", flat)
        self.assertIn("no breach projected", flat)

    def test_validation(self):
        self.assertEqual(headroom("--history", "1,2", "--lead-time-days", "1", *self.BASE).returncode, 2)
        self.assertEqual(headroom("--current", "5", "--lead-time-days", "1", *self.BASE).returncode, 2)
        self.assertEqual(headroom("--history", "1,2,3", "--lead-time-days", "1", "--period", "month",
                                  "--capacity", "100", "--as-of", "26/10/2026").returncode, 2)


if __name__ == "__main__":
    unittest.main()
