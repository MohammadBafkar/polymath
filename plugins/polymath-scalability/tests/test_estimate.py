"""Tests for capacity-estimation/scripts/estimate.py — the arithmetic the
capacity-estimation skill quotes.

Run with: python3 -m unittest discover -s plugins/polymath-scalability/tests
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills" / "capacity-estimation" / "scripts" / "estimate.py"
)

BASE = (
    "--dau", "5000000", "--actions-per-user-day", "20", "--read-ratio", "0.9",
    "--peak-factor", "3", "--read-bytes", "5000", "--write-bytes", "2000",
    "--retention-days", "365", "--replication", "3", "--cache-hit", "0.8",
)


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30)


class EstimateTest(unittest.TestCase):
    def test_worked_example(self):
        r = run(*BASE, "--per-node-qps", "2000", "--target-util", "0.6")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        self.assertIn("100.00M/day → avg 1,157 QPS → peak 3,472 QPS", out)
        self.assertIn("reads 3,125/s · writes 347/s", out)
        self.assertIn("972 QPS reach the data tier (625 read misses + 347 writes)", out)
        self.assertIn("ingress 0.69 MB/s (5.6 Mbit/s) · egress 15.62 MB/s (125.0 Mbit/s)", out)
        self.assertIn("10.00M writes/day → 21.90 TB over 365 d at ×3 replication", out)
        self.assertIn("ceil(3,472 ÷ (2000 × 0.6)) + 1 (N+1) = 4", out)

    def test_nodes_line_absent_without_per_node_qps(self):
        r = run(*BASE)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Nodes:", r.stdout)

    def test_cache_hit_zero_sends_every_read_to_origin(self):
        args = [a for a in BASE]
        args[args.index("--cache-hit") + 1] = "0"
        out = run(*args).stdout
        self.assertIn("3,472 QPS reach the data tier (3,125 read misses + 347 writes)", out)

    def test_all_reads_stores_nothing(self):
        args = list(BASE)
        args[args.index("--read-ratio") + 1] = "1"
        out = run(*args).stdout
        self.assertIn("0 writes/day", out)
        self.assertIn("0 B over 365 d", out)

    def test_validation(self):
        for bad in (
            ("--dau", "0", "--actions-per-user-day", "1", "--read-ratio", "0.5"),
            ("--dau", "10", "--actions-per-user-day", "1", "--read-ratio", "1.5"),
            ("--dau", "10", "--actions-per-user-day", "1", "--read-ratio", "0.5", "--cache-hit", "1"),
            ("--dau", "10", "--actions-per-user-day", "1", "--read-ratio", "0.5",
             "--per-node-qps", "100", "--target-util", "0"),
            ("--dau", "10", "--actions-per-user-day", "1", "--read-ratio", "0.5", "--peak-factor", "-1"),
        ):
            r = run(*bad)
            self.assertEqual(r.returncode, 2, bad)
            self.assertTrue(r.stderr.startswith("estimate:"), r.stderr)


if __name__ == "__main__":
    unittest.main()
