"""Unit tests for the feedback loop in bin/polymath-pipeline:
capture (conservative validation, 180d TTL) → digest → evaluate (verdict
needs evidence) → resolve, plus the TTL sweep and unknown-id rejection.

Run with: python3 -m unittest discover -s plugins/polymath-pipeline/tests
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest
from contextlib import redirect_stdout

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "plugins" / "polymath-pipeline" / "bin" / "polymath-pipeline"


def _import_engine():
    loader = importlib.machinery.SourceFileLoader("polymath_pipeline_fb", str(SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_pipeline_fb", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_engine()
        self._tmp = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.base / ".pdata")

    def tearDown(self) -> None:
        if self._prev_data is None:
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        else:
            os.environ["CLAUDE_PLUGIN_DATA"] = self._prev_data
        self._tmp.cleanup()

    def _run(self, *argv: str) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = self.mod.main(list(argv))
        return code, json.loads(buf.getvalue())

    def _capture_one(self, note: str = "Review ignored the tabs convention") -> str:
        code, out = self._run(
            "feedback", "capture",
            "--surface", "polymath-engineering:code-review",
            "--kind", "correction",
            "--note", note,
            "--evidence", "docs/conventions/review-checklist.md",
        )
        self.assertEqual(code, 0)
        self.assertTrue(out["captured"])
        return out["id"]

    def test_capture_digest_evaluate_resolve_lifecycle(self) -> None:
        fid = self._capture_one()
        code, digest = self._run("feedback", "digest")
        self.assertEqual(code, 0)
        self.assertEqual([i["id"] for i in digest["pending_evaluation"]], [fid])

        code, out = self._run(
            "feedback", "evaluate", fid,
            "--verdict", "valid-constructive",
            "--evidence", "Checked review-checklist.md; the Hard rule exists and was ignored",
        )
        self.assertEqual(code, 0)
        code, digest = self._run("feedback", "digest")
        self.assertEqual([i["id"] for i in digest["evaluated_unresolved"]], [fid])
        self.assertEqual(digest["pending_evaluation"], [])

        code, out = self._run(
            "feedback", "resolve", fid,
            "--outcome", "applied",
            "--detail", "skill_overrides entry added to .polymath/project.yaml",
        )
        self.assertEqual(code, 0)
        code, digest = self._run("feedback", "digest")
        self.assertEqual(digest["resolved"], 1)
        self.assertEqual(digest["evaluated_unresolved"], [])

    def test_capture_validates_kind_and_note(self) -> None:
        code, out = self._run(
            "feedback", "capture", "--surface", "x:y", "--kind", "rant", "--note", "n",
        )
        self.assertEqual(code, 2)
        self.assertFalse(out["captured"])
        code, out = self._run(
            "feedback", "capture", "--surface", "x:y", "--kind", "gap", "--note", "   ",
        )
        self.assertEqual(code, 2)

    def test_evaluate_requires_evidence_and_known_id(self) -> None:
        fid = self._capture_one()
        code, out = self._run(
            "feedback", "evaluate", fid, "--verdict", "invalid", "--evidence", "  ",
        )
        self.assertEqual(code, 2)
        code, out = self._run(
            "feedback", "evaluate", "nope123", "--verdict", "invalid", "--evidence", "x",
        )
        self.assertEqual(code, 2)
        self.assertIn("unknown or expired", out["reason"])

    def test_ttl_sweep_drops_expired_items(self) -> None:
        fid = self._capture_one()
        path = self.base / ".pdata" / "feedback.jsonl"
        stale = {
            "ts": "2025-01-01T00:00:00+00:00",
            "event": "capture",
            "id": "stale12345",
            "surface": "x:y",
            "kind": "gap",
            "note": "ancient",
            "evidence": None,
            "root": None,
        }
        path.write_text(json.dumps(stale) + "\n" + path.read_text())
        code, digest = self._run("feedback", "digest")
        self.assertEqual(digest["swept_expired"], 1)
        self.assertEqual([i["id"] for i in digest["pending_evaluation"]], [fid])
        # The expired item's events are physically gone.
        self.assertNotIn("stale12345", path.read_text())

    def test_resolve_proposed_catalog_patch_outcome(self) -> None:
        fid = self._capture_one("The catalog skill itself words the checklist wrong")
        self._run(
            "feedback", "evaluate", fid,
            "--verdict", "valid-constructive", "--evidence", "checked",
        )
        code, out = self._run(
            "feedback", "resolve", fid,
            "--outcome", "proposed-catalog-patch",
            "--detail", ".polymath/feedback/catalog-proposals/abc.md",
        )
        self.assertEqual(code, 0)
        self.assertEqual(out["outcome"], "proposed-catalog-patch")


if __name__ == "__main__":
    unittest.main()
