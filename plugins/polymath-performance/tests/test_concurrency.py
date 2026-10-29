"""Tests for high-load-io-design/scripts/concurrency.py — the Little's-law
arithmetic the high-load-io-design skill quotes.

Run with: python3 -m unittest discover -s plugins/polymath-performance/tests
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills" / "high-load-io-design" / "scripts" / "concurrency.py"
)


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30)


class ConcurrencyTest(unittest.TestCase):
    def test_pool_sizing(self):
        r = run("--rate", "800", "--latency-ms", "45", "--target-util", "0.7")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("800/s × 45 ms = 36.00 in flight", r.stdout)
        self.assertIn("ceil(36.00 ÷ 0.7) = 52 workers/connections", r.stdout)

    def test_thread_model_and_cpu_check(self):
        out = run("--rate", "800", "--latency-ms", "45", "--target-util", "0.7",
                  "--cpu-ms", "5", "--cores", "8").stdout
        self.assertIn("ceil(8 × 0.7 × (1 + 40/5)) = 51", out)
        self.assertIn("50% — OK", out)

    def test_cpu_over_target_is_flagged(self):
        out = run("--rate", "2000", "--latency-ms", "20", "--target-util", "0.7",
                  "--cpu-ms", "5", "--cores", "8").stdout
        self.assertIn("125% — OVER target", out)

    def test_queue_drain(self):
        out = run("--rate", "1000", "--capacity", "1500", "--backlog", "600000").stdout
        self.assertIn("600000 ÷ (1500 − 1000) = 20m 0s to drain", out)

    def test_queue_that_never_drains(self):
        out = run("--rate", "1200", "--capacity", "1000", "--backlog", "600000").stdout
        self.assertIn("never drains", out)

    def test_validation(self):
        for bad in (
            ("--rate", "0", "--latency-ms", "10"),
            ("--rate", "10"),
            ("--rate", "10", "--latency-ms", "10", "--target-util", "1.5"),
            ("--rate", "10", "--latency-ms", "10", "--cpu-ms", "5"),
            ("--rate", "10", "--latency-ms", "10", "--cpu-ms", "50", "--cores", "2"),
            ("--rate", "10", "--backlog", "5"),
            ("--rate", "10", "--capacity", "20"),
        ):
            r = run(*bad)
            self.assertEqual(r.returncode, 2, bad)
            self.assertTrue(r.stderr.startswith("concurrency:"), r.stderr)


if __name__ == "__main__":
    unittest.main()
