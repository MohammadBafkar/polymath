"""Tests for plan-review/scripts/plan-summary.py — deterministic plan JSON
classification that never prints values.

Run with: python3 -m unittest discover -s plugins/polymath-cloud/tests
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "plan-review" / "scripts" / "plan-summary.py"
SECRET = "hunter2-do-not-print"

PLAN = {
    "format_version": "1.2",
    "resource_changes": [
        {"address": "aws_db_instance.refund_primary", "type": "aws_db_instance",
         "action_reason": "replace_because_cannot_update",
         "change": {"actions": ["delete", "create"], "replace_paths": [["engine_version"]],
                    "after": {"password": SECRET}}},
        {"address": "aws_s3_bucket.legacy_uploads", "type": "aws_s3_bucket",
         "change": {"actions": ["delete"], "after": None}},
        {"address": "module.refunds.aws_sqs_queue.dlq", "type": "aws_sqs_queue",
         "change": {"actions": ["create"], "after": {"name": "refund-dlq"}}},
        {"address": "aws_iam_role_policy.worker", "type": "aws_iam_role_policy",
         "change": {"actions": ["update"], "after": {"policy": "{}"}}},
        {"address": "aws_security_group.web", "type": "aws_security_group",
         "change": {"actions": ["update"], "after": {"ingress": [{"cidr_blocks": ["0.0.0.0/0"]}]}}},
        {"address": "aws_instance.idle", "type": "aws_instance", "change": {"actions": ["no-op"]}},
    ],
    "resource_drift": [
        {"address": "aws_security_group.web", "change": {"actions": ["update"]}},
    ],
    "configuration": {"provider_config": {
        "aws": {"name": "aws", "version_constraint": "~> 5.0"},
        "random": {"name": "random"},
    }},
}


def run(plan: dict, *args: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(plan, fh)
    try:
        return subprocess.run([sys.executable, str(SCRIPT), fh.name, *args], capture_output=True, text=True, timeout=30)
    finally:
        pathlib.Path(fh.name).unlink()


class PlanSummaryTest(unittest.TestCase):
    def test_counts_and_terraform_cross_check(self):
        r = run(PLAN)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("create 1 · update 2 · replace 1 · delete 1", r.stdout)
        self.assertIn("2 to add, 2 to change, 2 to destroy", r.stdout)  # replace counts as add + destroy

    def test_replacement_cause_and_stateful_gate(self):
        out = run(PLAN).stdout
        self.assertRegex(out, r"aws_db_instance\.refund_primary\s+REPLACE  forced by: engine_version")
        self.assertIn("aws_s3_bucket.legacy_uploads (aws_s3_bucket) DELETE — data-loss gate", out)

    def test_iam_exposure_drift_providers(self):
        out = run(PLAN).stdout
        self.assertIn("- aws_iam_role_policy.worker update", out)
        self.assertIn("aws_security_group.web update — ingress open to the internet", out)
        self.assertIn("Drift (changed outside Terraform — not this PR's intent):\n  - aws_security_group.web update", out)
        self.assertIn("Providers without a version constraint: random", out)

    def test_never_prints_values(self):
        self.assertNotIn(SECRET, run(PLAN).stdout)

    def test_gates(self):
        self.assertIn("Minimum gate: apply-with-approval", run(PLAN).stdout)
        scoped = run(PLAN, "--scope", "module.refunds.*", "--scope", "aws_db_instance.*").stdout
        self.assertIn("- aws_s3_bucket.legacy_uploads delete", scoped)
        self.assertIn("Minimum gate: block", scoped)
        safe = {"format_version": "1.2", "resource_changes": [
            {"address": "aws_sqs_queue.q", "type": "aws_sqs_queue", "change": {"actions": ["create"], "after": {}}}]}
        self.assertIn("Minimum gate: apply-ok", run(safe).stdout)

    def test_rejects_non_plan(self):
        self.assertEqual(run({"hello": "world"}).returncode, 2)

    def test_deterministic(self):
        self.assertEqual(run(PLAN).stdout, run(PLAN).stdout)


if __name__ == "__main__":
    unittest.main()
