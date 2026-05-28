"""Unit tests for the capability layer in bin/polymath-flow.

Covers:
  - Workflow schema validation rejects unknown capabilities + malformed values
  - _resolve_capability_requirements happy path, mismatch, missing project
    config, unknown provider, workflow-pinned provider mismatch
  - _substitute honours ${capabilities.<cap>.<field>} placeholders
  - cmd_start fails fast (exit 2) when a required capability is unconfigured
  - state.json persists resolved capabilities for downstream use
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
FLOW_SCRIPT = REPO_ROOT / "plugins" / "polymath-flows" / "bin" / "polymath-flow"


def _import_flow():
    loader = importlib.machinery.SourceFileLoader("polymath_flow", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_flow", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_VOCAB = {
    "schemaVersion": 1,
    "capabilities": {
        "issue_tracker": {
            "description": "x",
            "providers": ["jira", "linear"],
            "providerPlugins": {
                "jira": "polymath-connector-jira",
                "linear": "polymath-connector-linear",
            },
        },
        "observability": {
            "description": "x",
            "providers": ["datadog", "honeycomb"],
            "providerPlugins": {
                "datadog": "polymath-connector-datadog",
                "honeycomb": "polymath-connector-monitoring",
            },
        },
    },
}


class CapabilityValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def _base_workflow(self, **extra) -> dict:
        wf = {
            "schemaVersion": 0.1,
            "name": "demo",
            "version": "0.1.0",
            "steps": [{"id": "s1", "invoke": "p:c", "prompt": "x"}],
        }
        wf.update(extra)
        return wf

    def test_unknown_capability_rejected(self) -> None:
        wf = self._base_workflow(
            requires={"capabilities": {"telemetry": True}}
        )
        errs = self.mod._validate(wf)
        self.assertTrue(
            any("unknown capability" in e for e in errs),
            f"expected rejection of unknown cap, got: {errs}",
        )

    def test_capability_value_must_be_true_or_object(self) -> None:
        for bad in ["jira", 42, None, False]:
            wf = self._base_workflow(
                requires={"capabilities": {"issue_tracker": bad}}
            )
            errs = self.mod._validate(wf)
            self.assertTrue(
                any("must be `true`" in e or "must be a mapping" in e for e in errs),
                f"bad value {bad!r} unexpectedly accepted: {errs}",
            )

    def test_capability_object_constraint_accepted(self) -> None:
        wf = self._base_workflow(
            requires={"capabilities": {"issue_tracker": {"provider": "jira"}}}
        )
        errs = self.mod._validate(wf)
        self.assertEqual(errs, [])

    def test_capability_object_unknown_key_rejected(self) -> None:
        wf = self._base_workflow(
            requires={"capabilities": {"issue_tracker": {"providers": "jira"}}}
        )
        errs = self.mod._validate(wf)
        self.assertTrue(any("unknown keys" in e for e in errs))

    def test_capability_provider_must_be_snake_case(self) -> None:
        wf = self._base_workflow(
            requires={"capabilities": {"issue_tracker": {"provider": "AzureDevOps"}}}
        )
        errs = self.mod._validate(wf)
        self.assertTrue(any("lower_snake_case" in e for e in errs))


class CapabilityResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_resolve_happy_path(self) -> None:
        wf = {
            "requires": {
                "capabilities": {
                    "issue_tracker": True,
                    "observability": {"provider": "datadog"},
                }
            }
        }
        project = {
            "schemaVersion": 1,
            "capabilities": {
                "issue_tracker": {"provider": "jira"},
                "observability": {"provider": "datadog"},
            },
        }
        plugins, resolved, errs = self.mod._resolve_capability_requirements(
            wf, project_caps=project, vocabulary=_VOCAB
        )
        self.assertEqual(errs, [])
        self.assertEqual(
            resolved["issue_tracker"],
            {"provider": "jira", "plugin": "polymath-connector-jira"},
        )
        self.assertEqual(
            resolved["observability"],
            {"provider": "datadog", "plugin": "polymath-connector-datadog"},
        )
        # Plugins list reflects both resolutions, no duplicates, in order.
        self.assertEqual(
            plugins,
            ["polymath-connector-jira", "polymath-connector-datadog"],
        )

    def test_resolve_workflow_pin_mismatch_fails(self) -> None:
        wf = {
            "requires": {
                "capabilities": {"observability": {"provider": "datadog"}}
            }
        }
        project = {
            "capabilities": {
                "observability": {"provider": "honeycomb"},
            }
        }
        _, _, errs = self.mod._resolve_capability_requirements(
            wf, project_caps=project, vocabulary=_VOCAB
        )
        self.assertTrue(
            any(
                "workflow pins provider" in e and "honeycomb" in e for e in errs
            ),
            f"expected mismatch error, got: {errs}",
        )

    def test_resolve_unconfigured_capability_fails(self) -> None:
        wf = {"requires": {"capabilities": {"issue_tracker": True}}}
        _, _, errs = self.mod._resolve_capability_requirements(
            wf, project_caps={}, vocabulary=_VOCAB
        )
        self.assertTrue(any("not configured" in e for e in errs), errs)

    def test_resolve_provider_not_in_vocabulary_fails(self) -> None:
        wf = {"requires": {"capabilities": {"observability": True}}}
        project = {
            "capabilities": {"observability": {"provider": "rollbar"}},
        }
        _, _, errs = self.mod._resolve_capability_requirements(
            wf, project_caps=project, vocabulary=_VOCAB
        )
        self.assertTrue(
            any("not in vocabulary providers" in e for e in errs), errs
        )

    def test_resolve_project_plugin_override_wins(self) -> None:
        wf = {"requires": {"capabilities": {"issue_tracker": True}}}
        project = {
            "capabilities": {
                "issue_tracker": {
                    "provider": "jira",
                    "plugin": "polymath-connector-jira-internal-fork",
                }
            }
        }
        plugins, resolved, errs = self.mod._resolve_capability_requirements(
            wf, project_caps=project, vocabulary=_VOCAB
        )
        self.assertEqual(errs, [])
        self.assertEqual(
            resolved["issue_tracker"]["plugin"],
            "polymath-connector-jira-internal-fork",
        )
        self.assertIn("polymath-connector-jira-internal-fork", plugins)


class CapabilitySubstitutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_substitute_capability_provider(self) -> None:
        caps = {
            "observability": {
                "provider": "datadog",
                "plugin": "polymath-connector-datadog",
            }
        }
        out = self.mod._substitute(
            "Query ${capabilities.observability.provider} for traces",
            inputs={}, workflow_meta={}, capabilities=caps,
        )
        self.assertEqual(out, "Query datadog for traces")

    def test_substitute_capability_plugin_in_invoke(self) -> None:
        caps = {
            "issue_tracker": {
                "provider": "jira",
                "plugin": "polymath-connector-jira",
            }
        }
        out = self.mod._substitute(
            "${capabilities.issue_tracker.plugin}:file-bug",
            inputs={}, workflow_meta={}, capabilities=caps,
        )
        self.assertEqual(out, "polymath-connector-jira:file-bug")

    def test_substitute_unknown_capability_leaves_intact(self) -> None:
        out = self.mod._substitute(
            "${capabilities.observability.provider}",
            inputs={}, workflow_meta={}, capabilities={},
        )
        # Unknown lookups expand to empty per the substitution contract — same
        # as inputs.x for an undeclared input. The contract is documented in
        # _substitute's docstring.
        self.assertEqual(out, "")

    def test_substitute_capabilities_optional(self) -> None:
        # When capabilities is None the substitution must not crash.
        out = self.mod._substitute(
            "literal",
            inputs={}, workflow_meta={}, capabilities=None,
        )
        self.assertEqual(out, "literal")


class CapabilityRunIntegrationTests(unittest.TestCase):
    """Exercise cmd_start with a temporary workflow + project config."""

    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)
        # Make project-layer workflow resolution point at our tmp tree.
        self.proj_wf_dir = self.work / ".claude" / "polymath" / "workflows"
        self.proj_wf_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        if self._prev_data is None:
            os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        else:
            os.environ["CLAUDE_PLUGIN_DATA"] = self._prev_data
        self._tmp.cleanup()

    def _capture(self, *argv: str) -> tuple[int, str, str]:
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr

        out_buf, err_buf = StringIO(), StringIO()
        code = 0
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            try:
                code = self.mod.main(list(argv))
            except SystemExit as e:
                code = int(e.code) if e.code is not None else 0
        return code, out_buf.getvalue(), err_buf.getvalue()

    def _write_workflow(self) -> None:
        (self.proj_wf_dir / "capDemo.yaml").write_text(
            "schemaVersion: 0.1\n"
            "name: capDemo\n"
            "version: 0.1.0\n"
            "requires:\n"
            "  capabilities:\n"
            "    issue_tracker: true\n"
            "steps:\n"
            "  - id: s1\n"
            "    invoke: ${capabilities.issue_tracker.plugin}:file-bug\n"
            "    prompt: file a bug in ${capabilities.issue_tracker.provider}\n"
        )

    def test_start_fails_when_capability_unconfigured(self) -> None:
        self._write_workflow()
        code, out, err = self._capture("start", "capDemo", "--input", "title=demo")
        self.assertEqual(code, 2)
        self.assertIn("issue_tracker", err)
        self.assertIn("not configured", err)

    def test_start_persists_resolved_capabilities(self) -> None:
        self._write_workflow()
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "capabilities.yaml").write_text(
            "schemaVersion: 1\n"
            "capabilities:\n"
            "  issue_tracker:\n"
            "    provider: jira\n"
            "    plugin: polymath-connector-jira\n"
        )
        code, out, _ = self._capture("start", "capDemo", "--input", "title=demo")
        self.assertEqual(code, 0, msg=out)
        run_id = json.loads(out)["run_id"]
        state = json.loads(
            (self.work / ".pdata" / "workflows" / run_id / "state.json").read_text()
        )
        self.assertEqual(
            state["capabilities"]["issue_tracker"]["provider"], "jira"
        )
        self.assertEqual(
            state["capabilities"]["issue_tracker"]["plugin"],
            "polymath-connector-jira",
        )
        self.assertIn("polymath-connector-jira", state["effective_plugins"])

        # `next` must expand placeholders against the resolved capability map.
        code, out, _ = self._capture("next", run_id)
        self.assertEqual(code, 0)
        step = json.loads(out)
        self.assertEqual(step["invoke"], "polymath-connector-jira:file-bug")
        self.assertEqual(step["prompt"], "file a bug in jira")


if __name__ == "__main__":
    unittest.main()
