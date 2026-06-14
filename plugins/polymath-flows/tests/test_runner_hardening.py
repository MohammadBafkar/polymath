"""Hardening tests for bin/polymath-flow.

  - Substituted values carrying shell metacharacters are refused, never
    interpolated into a shell command.
  - appStarts (which runs a repo-supplied smoke command) is skipped unless
    the repo opts in with a .polymath/trust marker / POLYMATH_ALLOW_SHELL.
  - command/commandSucceeds checks from a project/user-layer (untrusted)
    workflow are refused without the trust marker; marketplace workflows
    are trusted.
  - needs references are validated (dangling/self/forward) and serial
    ordering is enforced at completion time.
  - A corrupt/missing state.json yields exit code 3 (not a traceback), list
    skips a single bad run, and writes are atomic.

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
    loader = importlib.machinery.SourceFileLoader("polymath_flow_hardening", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class IsolatedCwd(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")
        self._prev_shell = os.environ.pop("POLYMATH_ALLOW_SHELL", None)
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        for key, prev in (("CLAUDE_PLUGIN_DATA", self._prev_data), ("POLYMATH_ALLOW_SHELL", self._prev_shell)):
            if prev is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prev
        self._tmp.cleanup()

    def _trust(self) -> None:
        (self.work / ".polymath").mkdir(exist_ok=True)
        (self.work / ".polymath" / "trust").write_text("")

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

    def _write_project_workflow(self, name: str, body: str) -> pathlib.Path:
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        path = wf_dir / f"{name}.yaml"
        path.write_text(body)
        return path


# --- shell-metachar guard

class ShellMetacharGuardTests(IsolatedCwd):
    def test_substitute_refuses_metachar_in_shell_context(self) -> None:
        with self.assertRaises(self.mod._ShellInjectionError):
            self.mod._substitute(
                "echo ${inputs.x}", inputs={"x": "; rm -rf /"},
                workflow_meta={}, shell_context=True,
            )

    def test_substitute_allows_safe_value_in_shell_context(self) -> None:
        out = self.mod._substitute(
            "test -s docs/${inputs.slug}.md", inputs={"slug": "rate-limit-login"},
            workflow_meta={}, shell_context=True,
        )
        self.assertEqual(out, "test -s docs/rate-limit-login.md")

    def test_non_shell_context_never_guards(self) -> None:
        # Prompts legitimately contain shell-ish text; no guard off the shell path.
        out = self.mod._substitute(
            "Run ${inputs.cmd}", inputs={"cmd": "a && b; c"}, workflow_meta={},
        )
        self.assertEqual(out, "Run a && b; c")

    def test_command_check_refuses_injected_input_without_executing(self) -> None:
        check = {"id": "c", "type": "commandSucceeds", "command": "echo ${inputs.x}"}
        outcome, detail = self.mod._run_check(
            check, self.work, {"x": "; touch HACKED #"}, {"slug": "x"},
        )
        self.assertIs(outcome, False)
        self.assertIn("refused", detail)
        self.assertFalse((self.work / "HACKED").exists())


# --- appStarts trust gate

class AppStartsTrustGateTests(IsolatedCwd):
    PROJECT = {"smoke": {"python": {"start": "true"}}}

    def test_appstarts_skipped_without_trust_marker(self) -> None:
        outcome, detail = self.mod._run_check(
            {"id": "b", "type": "appStarts", "lang": "python"}, self.work, {}, {},
            project=self.PROJECT,
        )
        self.assertEqual(outcome, "not-applicable")
        self.assertIn("trust", detail)

    def test_appstarts_runs_with_trust_marker(self) -> None:
        self._trust()
        outcome, _ = self.mod._run_check(
            {"id": "b", "type": "appStarts", "lang": "python"}, self.work, {}, {},
            project=self.PROJECT,
        )
        self.assertIs(outcome, True)  # one-shot `true` boots and exits 0

    def test_appstarts_runs_with_env_optin(self) -> None:
        os.environ["POLYMATH_ALLOW_SHELL"] = "1"
        outcome, _ = self.mod._run_check(
            {"id": "b", "type": "appStarts", "lang": "python"}, self.work, {}, {},
            project=self.PROJECT,
        )
        self.assertIs(outcome, True)


# --- workflow-source trust

class WorkflowSourceTrustTests(IsolatedCwd):
    def test_marketplace_workflow_is_trusted(self) -> None:
        mkt = self.mod.PLUGIN_ROOT / "workflows" / "shipFeature.yaml"
        self.assertTrue(self.mod._workflow_shell_trusted(mkt))

    def test_project_workflow_untrusted_without_marker(self) -> None:
        proj = self.work / ".claude" / "polymath" / "workflows" / "x.yaml"
        self.assertFalse(self.mod._workflow_shell_trusted(proj))

    def test_project_workflow_trusted_with_marker(self) -> None:
        self._trust()
        proj = self.work / ".claude" / "polymath" / "workflows" / "x.yaml"
        self.assertTrue(self.mod._workflow_shell_trusted(proj))

    def test_command_check_refused_when_untrusted(self) -> None:
        outcome, detail = self.mod._run_check(
            {"id": "c", "type": "commandSucceeds", "command": "true"},
            self.work, {}, {"slug": "x"}, workflow_trusted=False,
        )
        self.assertIs(outcome, False)
        self.assertIn("trust", detail)


# --- needs validation

class NeedsValidationTests(IsolatedCwd):
    def _wf(self, steps: list[dict]) -> dict:
        return {"schemaVersion": 0.1, "name": "x", "version": "1.0.0", "steps": steps}

    def test_dangling_needs_rejected(self) -> None:
        errs = self.mod._validate(self._wf([
            {"id": "a", "invoke": "x:y", "prompt": "p"},
            {"id": "b", "invoke": "x:y", "prompt": "p", "needs": ["nope"]},
        ]))
        self.assertTrue(any("not a prior step" in e for e in errs), errs)

    def test_forward_needs_rejected(self) -> None:
        errs = self.mod._validate(self._wf([
            {"id": "a", "invoke": "x:y", "prompt": "p", "needs": ["b"]},
            {"id": "b", "invoke": "x:y", "prompt": "p"},
        ]))
        self.assertTrue(any("not a prior step" in e for e in errs), errs)

    def test_self_needs_rejected(self) -> None:
        errs = self.mod._validate(self._wf([
            {"id": "a", "invoke": "x:y", "prompt": "p", "needs": ["a"]},
        ]))
        self.assertTrue(any("cannot reference itself" in e for e in errs), errs)

    def test_valid_backward_needs_accepted(self) -> None:
        errs = self.mod._validate(self._wf([
            {"id": "a", "invoke": "x:y", "prompt": "p"},
            {"id": "b", "invoke": "x:y", "prompt": "p", "needs": ["a"]},
        ]))
        self.assertFalse([e for e in errs if "needs" in e], errs)


# --- serial ordering

ORDER_FLOW = (
    "schemaVersion: 0.1\n"
    "name: orderFlow\n"
    "version: 0.1.0\n"
    "steps:\n"
    "  - id: step-a\n    invoke: a:b\n    prompt: A\n"
    "  - id: step-b\n    invoke: a:b\n    prompt: B\n    needs: [step-a]\n"
    "  - id: step-c\n    invoke: a:b\n    prompt: C\n    needs: [step-b]\n"
)


class SerialOrderingTests(IsolatedCwd):
    def _start(self) -> str:
        self._write_project_workflow("orderFlow", ORDER_FLOW)
        code, out = self._capture("start", "orderFlow")
        self.assertEqual(code, 0, out)
        return json.loads(out)["run_id"]

    def _state(self, run_id: str) -> dict:
        return json.loads(
            (self.work / ".pdata" / "workflows" / run_id / "state.json").read_text()
        )

    def test_out_of_order_completion_refused(self) -> None:
        run_id = self._start()
        code, out = self._capture("complete", run_id, "step-c")
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out)["status"], "refused")
        state = self._state(run_id)
        self.assertEqual(state["status"], "active")
        self.assertTrue(all(s["status"] == "pending" for s in state["steps"]))

    def test_in_order_completion_advances_to_completed(self) -> None:
        run_id = self._start()
        for sid in ("step-a", "step-b", "step-c"):
            code, _ = self._capture("complete", run_id, sid)
            self.assertEqual(code, 0)
        code, out = self._capture("next", run_id)  # no mustPass -> asserts completed
        self.assertEqual(code, 0)
        self.assertEqual(self._state(run_id)["status"], "completed")


# --- state corruption + atomic writes

class StateCorruptionTests(IsolatedCwd):
    def _start_order_flow(self) -> str:
        self._write_project_workflow("orderFlow", ORDER_FLOW)
        code, out = self._capture("start", "orderFlow")
        self.assertEqual(code, 0, out)
        return json.loads(out)["run_id"]

    def test_corrupt_state_yields_exit_3(self) -> None:
        run_id = self._start_order_flow()
        sp = self.work / ".pdata" / "workflows" / run_id / "state.json"
        sp.write_text("not valid json {{{")
        code, _ = self._capture("next", run_id)
        self.assertEqual(code, 3)

    def test_list_skips_single_corrupt_run(self) -> None:
        good = self._start_order_flow()
        bad_dir = self.work / ".pdata" / "workflows" / "broken-run"
        bad_dir.mkdir(parents=True, exist_ok=True)
        (bad_dir / "state.json").write_text("}{ corrupt")
        code, out = self._capture("list")
        self.assertEqual(code, 0)
        listed = {r["run_id"] for r in json.loads(out)}
        self.assertIn(good, listed)
        self.assertNotIn("broken-run", listed)

    def test_write_state_is_atomic_and_leaves_no_tmp(self) -> None:
        run_dir = self.work / ".pdata" / "workflows" / "r"
        run_dir.mkdir(parents=True, exist_ok=True)
        self.mod._write_state(run_dir, {"run_id": "r", "status": "active"})
        self.assertEqual(json.loads((run_dir / "state.json").read_text())["status"], "active")
        self.assertFalse((run_dir / "state.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
