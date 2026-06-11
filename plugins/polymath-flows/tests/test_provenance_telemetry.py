"""Unit tests for Phase 4 runner additions in bin/polymath-flow:

  - run provenance: `provenance.runs: true` in the frozen snapshot
    whole-copies the completed run record into `.polymath/runs/<run_id>/`
    (opt-in, fail-open, never on opt-out or outside a .polymath repo)
  - opt-in local telemetry: POLYMATH_TELEMETRY=1 appends one JSONL line
    per invocation (command + workflow name + duration + outcome, nothing
    else); unset or any other value writes NOTHING — the docs/PRIVACY.md
    off-state gate

Run with: python3 -m unittest discover -s plugins/polymath-flows/tests
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import pathlib
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
FLOW_SCRIPT = REPO_ROOT / "plugins" / "polymath-flows" / "bin" / "polymath-flow"

TINY_FLOW = (
    "schemaVersion: 0.1\n"
    "name: tinyFlow\n"
    "version: 0.1.0\n"
    "steps:\n"
    "  - id: only\n"
    "    invoke: a:b\n"
    "    prompt: Do the thing.\n"
)


def _import_flow():
    loader = importlib.machinery.SourceFileLoader("polymath_flow_p4", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_flow_p4", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Phase4TestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._env = {
            k: os.environ.get(k) for k in ("CLAUDE_PLUGIN_DATA", "POLYMATH_TELEMETRY")
        }
        self.pdata = self.work / ".pdata"
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.pdata)
        os.environ.pop("POLYMATH_TELEMETRY", None)
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)
        (self.work / ".polymath").mkdir()
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "tinyFlow.yaml").write_text(TINY_FLOW)

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self._tmp.cleanup()

    def _capture(self, *argv: str) -> tuple[int, str]:
        from contextlib import redirect_stdout
        from io import StringIO

        buf = StringIO()
        code = 0
        with redirect_stdout(buf):
            try:
                code = self.mod.main(list(argv))
            except SystemExit as e:
                code = int(e.code) if e.code is not None else 0
        return code, buf.getvalue()

    def _write_snapshot(self, runs: bool) -> None:
        snap_dir = self.pdata / "polymath-core"
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "project-context.json").write_text(
            json.dumps({"schemaVersion": 1, "provenance": {"runs": runs}})
        )

    def _walk_tiny_flow(self) -> tuple[str, dict]:
        code, out = self._capture("start", "tinyFlow")
        self.assertEqual(code, 0, out)
        run_id = json.loads(out)["run_id"]
        code, _ = self._capture("complete", run_id, "only", "--summary", "done")
        self.assertEqual(code, 0)
        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 0, out)
        return run_id, json.loads(out)


class RunProvenanceTests(Phase4TestCase):
    def test_opt_in_whole_copies_completed_run(self) -> None:
        self._write_snapshot(runs=True)
        run_id, result = self._walk_tiny_flow()
        dest = self.work.resolve() / ".polymath" / "runs" / run_id
        self.assertEqual(result.get("provenance"), str(dest))
        # Whole copy: every part of the run record is present.
        self.assertTrue((dest / "state.json").is_file())
        self.assertTrue((dest / "inputs.json").is_file())
        self.assertTrue((dest / "trace.jsonl").is_file())
        self.assertTrue((dest / "step-summaries" / "only.md").is_file())
        self.assertTrue((dest / "artifacts").is_dir())
        state = json.loads((dest / "state.json").read_text())
        self.assertEqual(state["status"], "completed")

    def test_opt_out_copies_nothing(self) -> None:
        self._write_snapshot(runs=False)
        run_id, result = self._walk_tiny_flow()
        self.assertNotIn("provenance", result)
        self.assertFalse((self.work / ".polymath" / "runs").exists())

    def test_no_snapshot_copies_nothing(self) -> None:
        run_id, result = self._walk_tiny_flow()
        self.assertNotIn("provenance", result)
        self.assertFalse((self.work / ".polymath" / "runs").exists())

    def test_fail_open_when_dest_unwritable(self) -> None:
        self._write_snapshot(runs=True)
        # A FILE where the runs dir should go makes copytree fail.
        (self.work / ".polymath" / "runs").write_text("not a directory")
        run_id, result = self._walk_tiny_flow()
        self.assertEqual(result["status"], "completed")  # run still completes
        self.assertNotIn("provenance", result)


class TelemetryTests(Phase4TestCase):
    def _telemetry_path(self) -> pathlib.Path:
        return self.pdata / "telemetry.jsonl"

    def test_off_by_default_writes_nothing(self) -> None:
        self._capture("list")
        self.assertFalse(self._telemetry_path().exists())

    def test_zero_disables(self) -> None:
        os.environ["POLYMATH_TELEMETRY"] = "0"
        self._capture("list")
        self.assertFalse(self._telemetry_path().exists())

    def test_opt_in_writes_capped_payload(self) -> None:
        os.environ["POLYMATH_TELEMETRY"] = "1"
        self._capture("start", "tinyFlow", "--input", "title=Secret Title")
        lines = self._telemetry_path().read_text().splitlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["tool"], "polymath-flow")
        self.assertEqual(record["cmd"], "start")
        self.assertEqual(record["exit"], 0)
        self.assertEqual(record["workflow"], "tinyFlow")
        self.assertIn("duration_ms", record)
        # Payload cap: no run ids (slug derives from the user's title), no
        # inputs, no content of any kind.
        self.assertEqual(
            set(record.keys()),
            {"ts", "tool", "cmd", "exit", "duration_ms", "workflow"},
        )
        self.assertNotIn("Secret", json.dumps(record))

    def test_failure_exit_recorded(self) -> None:
        os.environ["POLYMATH_TELEMETRY"] = "1"
        self._capture("next", "no-such-run")
        records = [json.loads(l) for l in self._telemetry_path().read_text().splitlines()]
        self.assertEqual(records[-1]["cmd"], "next")
        self.assertEqual(records[-1]["exit"], 3)


if __name__ == "__main__":
    unittest.main()
