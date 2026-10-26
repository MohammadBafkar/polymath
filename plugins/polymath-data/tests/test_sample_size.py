"""Tests for run-experiment/scripts/sample-size.py — sizing, duration, SRM.

Run with: python3 -m unittest discover -s plugins/polymath-data/tests
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "run-experiment" / "scripts" / "sample-size.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30)


def load():
    spec = importlib.util.spec_from_file_location("sample_size", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SizingTest(unittest.TestCase):
    def test_mean(self):
        r = run("--metric", "mean", "--sigma", "2000", "--mde", "100", "--daily-eligible", "80000")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("n per variant: 6,280", r.stdout)  # 2 × 2.8016² × 2000² / 100²
        self.assertIn("run 7 days", r.stdout)
        self.assertIn("Verdict:  OK", r.stdout)

    def test_proportion_matches_reference_calculators(self):
        out = run("--metric", "proportion", "--baseline", "0.10", "--mde", "0.02").stdout
        self.assertIn("n per variant: 3,841", out)  # 10% → 12%, α .05, power .8
        self.assertIn("[TBD: daily eligible units", out)

    def test_relative_mde_and_underpowered(self):
        out = run("--metric", "proportion", "--baseline", "0.12", "--mde-relative", "2",
                  "--daily-eligible", "30000", "--allocation", "0.5").stdout
        self.assertIn("UNDERPOWERED — needs 42 days", out)
        self.assertIn("detectable MDE is", out)

    def test_bonferroni_for_three_variants(self):
        out = run("--metric", "mean", "--sigma", "10", "--mde", "1", "--variants", "3").stdout
        self.assertIn("α per comparison = 0.025", out)
        self.assertIn("z(1−α/2) = 2.241", out)

    def test_whole_weeks(self):
        # n = 1,570 per variant; 2 × 1,570 / 200 per day = 15.70 days → rounds up to 3 weeks.
        out = run("--metric", "mean", "--sigma", "10", "--mde", "1", "--daily-eligible", "200").stdout
        self.assertIn("n per variant: 1,570", out)
        self.assertIn("15.70 days of traffic → run 21 days", out)

    def test_validation(self):
        self.assertEqual(run("--metric", "mean", "--mde", "1").returncode, 2)  # no sigma
        self.assertEqual(run("--metric", "proportion", "--baseline", "0.99", "--mde", "0.02").returncode, 2)
        self.assertEqual(run().returncode, 2)


class SrmTest(unittest.TestCase):
    def test_chi_square_tail_matches_tables(self):
        mod = load()
        for x, df, p in [(3.841459, 1, 0.05), (5.991465, 2, 0.05), (11.34487, 3, 0.01), (10.82757, 1, 0.001)]:
            self.assertAlmostEqual(mod.chi2_sf(x, df), p, places=5)

    def test_verdicts(self):
        self.assertIn("no SRM", run("--srm", "50421,49579").stdout)  # p ≈ 0.0078
        self.assertIn("SRM DETECTED", run("--srm", "51000,49000").stdout)  # p ≈ 2.5e-10
        self.assertIn("no SRM", run("--srm", "9000,1000", "--split", "90,10").stdout)


if __name__ == "__main__":
    unittest.main()
