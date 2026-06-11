"""Unit tests for the Phase 2 gate types and guard execution in
bin/polymath-flow.

Covers:
  - connectorAvailable: configured / unconfigured / provider pin
  - appStarts: not-applicable resolutions, one-shot pass/fail, boot-log
    readiness, multi-recipe lang requirement, missing credentials file
  - the `not_applicable` array in assert output (reported, never blocking)
  - guards at start: blocking failure refuses the run (no state littered),
    advisory failure reports but starts, connectorAvailable as a guard

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


def _import_flow():
    loader = importlib.machinery.SourceFileLoader("polymath_flow_gates", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_flow_gates", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class IsolatedCwdTestCase(unittest.TestCase):
    """Temp cwd + temp CLAUDE_PLUGIN_DATA, so neither this repo's .polymath/
    nor real plugin data leaks into gate evaluation."""

    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        if self._prev_data is None:
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        else:
            os.environ["CLAUDE_PLUGIN_DATA"] = self._prev_data
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

    def _write_capabilities(self, body: str) -> None:
        cap_dir = self.work / ".polymath"
        cap_dir.mkdir(exist_ok=True)
        (cap_dir / "capabilities.yaml").write_text(body)


class ConnectorAvailableTests(IsolatedCwdTestCase):
    def test_unconfigured_capability_fails(self) -> None:
        outcome, detail = self.mod._run_connector_available(
            {"id": "g", "type": "connectorAvailable", "capability": "issue_tracker"}
        )
        self.assertIs(outcome, False)
        self.assertIn("no provider configured", detail)

    def test_configured_capability_passes(self) -> None:
        self._write_capabilities(
            "capabilities:\n"
            "  issue_tracker:\n"
            "    provider: jira\n"
            "    plugin: polymath-tracker\n"
        )
        outcome, detail = self.mod._run_connector_available(
            {"id": "g", "type": "connectorAvailable", "capability": "issue_tracker"}
        )
        self.assertIs(outcome, True)
        self.assertIn("provider=jira", detail)

    def test_provider_pin_mismatch_fails(self) -> None:
        self._write_capabilities(
            "capabilities:\n"
            "  issue_tracker:\n"
            "    provider: jira\n"
            "    plugin: polymath-tracker\n"
        )
        outcome, detail = self.mod._run_connector_available(
            {
                "id": "g",
                "type": "connectorAvailable",
                "capability": "issue_tracker",
                "provider": "linear",
            }
        )
        self.assertIs(outcome, False)
        self.assertIn("does not match", detail)

    def test_unknown_capability_fails(self) -> None:
        outcome, detail = self.mod._run_connector_available(
            {"id": "g", "type": "connectorAvailable", "capability": "telepathy"}
        )
        self.assertIs(outcome, False)
        self.assertIn("unknown capability", detail)


class AppStartsTests(IsolatedCwdTestCase):
    def test_no_snapshot_is_not_applicable(self) -> None:
        outcome, detail = self.mod._run_app_starts({"id": "b", "type": "appStarts"}, None)
        self.assertEqual(outcome, "not-applicable")
        self.assertIn("no smoke recipes", detail)

    def test_missing_lang_recipe_is_not_applicable(self) -> None:
        project = {"smoke": {"python": {"start": "true"}}}
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts", "lang": "go"}, project
        )
        self.assertEqual(outcome, "not-applicable")
        self.assertIn("lang='go'", detail)

    def test_multiple_recipes_require_lang(self) -> None:
        project = {"smoke": {"python": {"start": "true"}, "node": {"start": "true"}}}
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        self.assertIs(outcome, False)
        self.assertIn("needs 'lang'", detail)

    def test_one_shot_start_pass_and_fail(self) -> None:
        ok_project = {"smoke": {"python": {"start": "true", "timeout_seconds": 5}}}
        outcome, _ = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, ok_project
        )
        self.assertIs(outcome, True)

        bad_project = {"smoke": {"python": {"start": "false", "timeout_seconds": 5}}}
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, bad_project
        )
        self.assertIs(outcome, False)
        self.assertIn("rc=1", detail)

    def test_boot_log_pattern_readiness(self) -> None:
        project = {
            "smoke": {
                "python": {
                    "start": "echo BOOT_OK && sleep 30",
                    "readiness": "BOOT_OK",
                    "timeout_seconds": 10,
                }
            }
        }
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        self.assertIs(outcome, True, detail)
        self.assertIn("boot log matched", detail)

    def test_boot_log_pattern_fails_fast_on_clean_exit(self) -> None:
        project = {
            "smoke": {
                "python": {
                    "start": "echo nothing-here",
                    "readiness": "NEVER_PRINTED",
                    "timeout_seconds": 30,
                }
            }
        }
        import time

        t0 = time.monotonic()
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        elapsed = time.monotonic() - t0
        self.assertIs(outcome, False)
        self.assertLess(elapsed, 10, "must fail fast once the starter exited")

    def test_missing_credentials_file_is_not_applicable(self) -> None:
        project = {
            "smoke": {
                "python": {
                    "start": "true",
                    "credentials_file": ".env.smoke.missing",
                }
            }
        }
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        self.assertEqual(outcome, "not-applicable")
        self.assertIn("credentials_file", detail)

    def test_readiness_path_without_port_fails(self) -> None:
        project = {"smoke": {"python": {"start": "true", "readiness": "/health"}}}
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        self.assertIs(outcome, False)
        self.assertIn("no port", detail)

    def test_detached_server_torn_down_after_gate(self) -> None:
        """A starter that backgrounds the real server and exits must not
        leak the server: the whole process group is signalled even when
        the leader is already gone — otherwise the orphan holds the port
        and the NEXT appStarts run false-passes against the stale app."""
        import socket
        import time

        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        project = {
            "smoke": {
                "python": {
                    "start": (
                        f"python3 -m http.server {port} --bind 127.0.0.1 "
                        f"& echo launched"
                    ),
                    "port": port,
                    "timeout_seconds": 15,
                }
            }
        }
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        self.assertIs(outcome, True, detail)
        # The detached server must be gone shortly after the gate returns.
        deadline = time.monotonic() + 5
        alive = True
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    pass
                time.sleep(0.2)
            except OSError:
                alive = False
                break
        self.assertFalse(alive, "detached server leaked past the gate teardown")

    def test_non_utf8_credentials_file_is_not_applicable(self) -> None:
        cred = self.work / ".env.smoke"
        cred.write_bytes(b"PASSWORD=caf\xe9\n")
        project = {
            "smoke": {
                "python": {"start": "true", "credentials_file": str(cred)}
            }
        }
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"}, project
        )
        self.assertEqual(outcome, "not-applicable")
        self.assertIn("unreadable", detail)

    def test_junk_timeout_and_port_do_not_crash(self) -> None:
        outcome, _ = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"},
            {"smoke": {"py": {"start": "true", "timeout_seconds": "sixty"}}},
        )
        self.assertIs(outcome, True)
        outcome, detail = self.mod._run_app_starts(
            {"id": "b", "type": "appStarts"},
            {"smoke": {"py": {"start": "true", "port": "http"}}},
        )
        self.assertIs(outcome, False)
        self.assertIn("not an integer", detail)


class NotApplicableReportingTests(IsolatedCwdTestCase):
    """not-applicable is reported in assert output and never blocks."""

    def _assert_result(self, workflow: dict) -> tuple[int, dict]:
        import contextlib
        import io

        run_dir = self.work / ".pdata" / "workflows" / "na-run"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "state.json").write_text(
            json.dumps({"run_id": "na-run", "status": "active", "steps": []})
        )
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = self.mod._assert(run_dir, workflow, {}, {"slug": "x"})
        return rc, json.loads(buf.getvalue())

    def test_not_applicable_does_not_block_completion(self) -> None:
        rc, out = self._assert_result(
            {
                "name": "x",
                "mustPass": [
                    {"id": "boots", "type": "appStarts"},
                    {"id": "real", "type": "commandSucceeds", "command": "true"},
                ],
            }
        )
        self.assertEqual(rc, 0)
        self.assertEqual(out["status"], "completed")
        self.assertEqual([n["id"] for n in out["not_applicable"]], ["boots"])
        self.assertEqual(out["advisories"], [])

    def test_not_applicable_reported_alongside_failures(self) -> None:
        rc, out = self._assert_result(
            {
                "name": "x",
                "mustPass": [
                    {"id": "boots", "type": "appStarts"},
                    {"id": "real", "type": "commandSucceeds", "command": "false"},
                ],
            }
        )
        self.assertEqual(rc, 2)
        self.assertEqual(out["status"], "paused")
        self.assertEqual([f["id"] for f in out["failures"]], ["real"])
        self.assertEqual([n["id"] for n in out["not_applicable"]], ["boots"])

    def test_result_omits_not_applicable_when_empty(self) -> None:
        rc, out = self._assert_result(
            {
                "name": "x",
                "mustPass": [
                    {"id": "real", "type": "commandSucceeds", "command": "true"},
                ],
            }
        )
        self.assertEqual(rc, 0)
        self.assertNotIn("not_applicable", out)


class GuardExecutionTests(IsolatedCwdTestCase):
    def _write_workflow(self, name: str, guards_yaml: str) -> None:
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        (wf_dir / f"{name}.yaml").write_text(
            "schemaVersion: 0.1\n"
            f"name: {name}\n"
            "version: 0.1.0\n"
            f"{guards_yaml}"
            "steps:\n"
            "  - id: only\n"
            "    invoke: a:b\n"
            "    prompt: Do the thing.\n"
        )

    def test_blocking_guard_failure_refuses_start(self) -> None:
        self._write_workflow(
            "guardedFlow",
            "guards:\n"
            "  - id: never\n"
            "    type: command\n"
            "    command: \"false\"\n",
        )
        code, out = self._capture("start", "guardedFlow")
        self.assertEqual(code, 2)
        result = json.loads(out)
        self.assertEqual(result["status"], "guard-failed")
        self.assertEqual([f["id"] for f in result["failures"]], ["never"])
        # No run state littered.
        runs = self.work / ".pdata" / "workflows"
        self.assertFalse(
            runs.exists() and any(runs.iterdir()),
            "a refused start must not create a run directory",
        )

    def test_advisory_guard_failure_reports_but_starts(self) -> None:
        self._write_workflow(
            "advisoryFlow",
            "guards:\n"
            "  - id: soft\n"
            "    type: command\n"
            "    command: \"false\"\n"
            "    severity: advisory\n",
        )
        code, out = self._capture("start", "advisoryFlow")
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result["status"], "active")
        self.assertEqual([a["id"] for a in result["guard_advisories"]], ["soft"])

    def test_passing_guard_starts_clean(self) -> None:
        self._write_workflow(
            "cleanFlow",
            "guards:\n"
            "  - id: ready\n"
            "    type: command\n"
            "    command: \"true\"\n",
        )
        code, out = self._capture("start", "cleanFlow")
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result["status"], "active")
        self.assertNotIn("guard_advisories", result)

    def test_connector_available_guard_blocks_unconfigured(self) -> None:
        self._write_workflow(
            "connectorFlow",
            "guards:\n"
            "  - id: tracker-on\n"
            "    type: connectorAvailable\n"
            "    capability: issue_tracker\n",
        )
        code, out = self._capture("start", "connectorFlow")
        self.assertEqual(code, 2)
        result = json.loads(out)
        self.assertEqual(result["status"], "guard-failed")
        self.assertIn("no provider configured", result["failures"][0]["detail"])

        # Configure the capability; the same start now passes the guard.
        self._write_capabilities(
            "capabilities:\n"
            "  issue_tracker:\n"
            "    provider: jira\n"
            "    plugin: polymath-tracker\n"
        )
        code, out = self._capture("start", "connectorFlow")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["status"], "active")

    def test_step_summary_matches_rejected_in_guards(self) -> None:
        """No step summaries exist before any step has run, so a
        stepSummaryMatches guard could never pass — validation rejects it."""
        errs = self.mod._validate(
            {
                "schemaVersion": 0.1,
                "name": "x",
                "version": "1.0.0",
                "steps": [{"id": "s", "invoke": "a:b", "prompt": "p"}],
                "guards": [
                    {"id": "g", "type": "stepSummaryMatches", "step": "s", "pattern": "x"}
                ],
            }
        )
        self.assertTrue(any("cannot be a guard" in e for e in errs))

    def test_app_starts_guard_not_applicable_starts(self) -> None:
        self._write_workflow(
            "bootFlow",
            "guards:\n"
            "  - id: boots\n"
            "    type: appStarts\n",
        )
        code, out = self._capture("start", "bootFlow")
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result["status"], "active")
        self.assertEqual([n["id"] for n in result["not_applicable"]], ["boots"])


if __name__ == "__main__":
    unittest.main()
