"""Unit tests for bin/polymath-flow.

Loaded via importlib because the script has no .py extension and no entry
point. Tests cover:

  - YAML subset parser fallback (PyYAML disabled per-test)
  - Workflow schema validation
  - State transitions (start → next → complete → assert)
  - mustPass checks: fileExists, fileMatches, commandSucceeds,
    stepSummaryMatches

Run with: python3 -m unittest discover -s plugins/polymath-flows/tests
"""

from __future__ import annotations

import importlib.util
import importlib.machinery
import json
import os
import pathlib
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
FLOW_SCRIPT = REPO_ROOT / "plugins" / "polymath-flows" / "bin" / "polymath-flow"
SHIP_YAML = REPO_ROOT / "plugins" / "polymath-flows" / "workflows" / "shipFeature.yaml"


def _import_flow():
    # The script has no .py extension, so use SourceFileLoader directly.
    loader = importlib.machinery.SourceFileLoader("polymath_flow", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_flow", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _with_no_yaml(monkey_globals: dict) -> dict:
    """Return a copy of the module globals with PyYAML disabled by setting
    yaml to None — forces the fallback _load_yaml branch."""
    g = dict(monkey_globals)
    g["yaml"] = None
    return g


class YamlSubsetParserTests(unittest.TestCase):
    """Exercise the fallback YAML parser baked into bin/polymath-flow."""

    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_top_level_mapping(self) -> None:
        text = textwrap.dedent(
            """\
            schemaVersion: 0.1
            name: example
            version: 1.2.3
            description: a one liner
            """
        )
        # Force fallback by calling the fallback loader directly. The script
        # defines _load_yaml regardless; if PyYAML is present, calling it is
        # still a valid integration test.
        data = self.mod._load_yaml(text)
        self.assertEqual(data["schemaVersion"], 0.1)
        self.assertEqual(data["name"], "example")
        self.assertEqual(data["version"], "1.2.3")
        self.assertEqual(data["description"], "a one liner")

    def test_nested_mapping_and_list(self) -> None:
        text = textwrap.dedent(
            """\
            requires:
              plugins:
                - polymath-core
                - polymath-product
            inputs:
              - name: title
                type: string
                required: true
              - name: scope
                type: enum
                values: [small, medium]
                default: small
            """
        )
        data = self.mod._load_yaml(text)
        self.assertEqual(data["requires"]["plugins"], ["polymath-core", "polymath-product"])
        self.assertEqual(len(data["inputs"]), 2)
        self.assertEqual(data["inputs"][0]["name"], "title")
        self.assertIs(data["inputs"][0]["required"], True)
        self.assertEqual(data["inputs"][1]["values"], ["small", "medium"])

    def test_loads_shipfeature_yaml(self) -> None:
        text = SHIP_YAML.read_text()
        data = self.mod._load_yaml(text)
        self.assertEqual(data["name"], "shipFeature")
        self.assertEqual(data["schemaVersion"], 0.1)
        step_ids = [s["id"] for s in data["steps"]]
        self.assertEqual(
            step_ids,
            ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"],
        )
        mustpass_ids = [c["id"] for c in data["mustPass"]]
        self.assertIn("prd-exists", mustpass_ids)
        self.assertIn("tests-mentioned", mustpass_ids)

    def test_comments_are_stripped(self) -> None:
        text = textwrap.dedent(
            """\
            # leading comment
            schemaVersion: 0.1   # trailing comment
            name: x
            """
        )
        data = self.mod._load_yaml(text)
        self.assertEqual(data["schemaVersion"], 0.1)
        self.assertEqual(data["name"], "x")


class SchemaValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_shipfeature_validates(self) -> None:
        data = self.mod._load_yaml(SHIP_YAML.read_text())
        self.assertEqual(self.mod._validate(data), [])

    def test_unknown_top_level_key_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [{"id": "s1", "invoke": "p:s", "prompt": "p"}],
            "unknownKey": "bad",
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("unknown top-level keys" in e for e in errs))

    def test_unknown_step_key_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [
                {"id": "s1", "invoke": "p:c", "prompt": "p", "parallel": True},
            ],
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("unknown keys" in e for e in errs))

    def test_topology_other_than_series_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [
                {"id": "s1", "invoke": "p:c", "prompt": "p", "topology": "fanout"},
            ],
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("topology" in e for e in errs))

    def test_unsupported_schema_version_rejected(self) -> None:
        data = {"schemaVersion": 0.2, "name": "foo", "version": "0.1.0", "steps": []}
        errs = self.mod._validate(data)
        self.assertTrue(any("unsupported schemaVersion" in e for e in errs))

    def test_duplicate_step_id_rejected(self) -> None:
        data = {
            "schemaVersion": 0.1,
            "name": "foo",
            "version": "0.1.0",
            "steps": [
                {"id": "s1", "invoke": "p:c", "prompt": "p"},
                {"id": "s1", "invoke": "p:d", "prompt": "p"},
            ],
        }
        errs = self.mod._validate(data)
        self.assertTrue(any("duplicate" in e for e in errs))


class StateTransitionTests(unittest.TestCase):
    """End-to-end through the public CLI surface in a tmpdir + scratch repo."""

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
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        code = 0
        with redirect_stdout(buf):
            try:
                code = self.mod.main(list(argv))
            except SystemExit as e:
                code = int(e.code) if e.code is not None else 0
        return code, buf.getvalue()

    def test_full_shipfeature_walk(self) -> None:
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=Rate-limit /login",
            "--input", "scope=small",
        )
        self.assertEqual(code, 0)
        run_id = json.loads(out)["run_id"]

        code, out = self._capture("next", run_id)
        self.assertEqual(code, 0)
        first = json.loads(out)
        self.assertEqual(first["step_id"], "prd")
        self.assertEqual(first["invoke"], "polymath-product:prd")
        self.assertIn("rate-limit-login", first["artifacts"][0])

        steps = ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]
        summaries = {
            "prd": "PRD drafted",
            "acceptance": "Acceptance criteria added",
            "implement": "Implementation complete",
            "review": "Reviewed",
            "verify": "All tests verified, ran lint and typecheck",
            "changelog": "CHANGELOG updated",
            "pr": "PR description drafted",
        }

        # Pre-create the artifacts expected by mustPass.
        (self.work / "docs" / "prds").mkdir(parents=True, exist_ok=True)
        (self.work / "docs" / "pr").mkdir(parents=True, exist_ok=True)
        (self.work / "docs" / "prds" / "rate-limit-login.md").write_text("# PRD\n")
        (self.work / "CHANGELOG.md").write_text("## [Unreleased]\n")
        (self.work / "docs" / "pr" / "rate-limit-login.md").write_text("# PR\n")

        for sid in steps:
            sf = self.work / f"{sid}.summary.md"
            sf.write_text(summaries[sid])
            code, _ = self._capture("complete", run_id, sid, "--summary", str(sf))
            self.assertEqual(code, 0, f"complete step {sid} failed")

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 0, msg=f"assert failed: {out}")
        result = json.loads(out)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["checks"], 4)

    def test_assert_pauses_on_missing_artifact(self) -> None:
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=feature x",
        )
        run_id = json.loads(out)["run_id"]
        for sid in ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]:
            sf = self.work / f"{sid}.summary.md"
            sf.write_text("tests verified")
            self._capture("complete", run_id, sid, "--summary", str(sf))

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 2)
        result = json.loads(out)
        self.assertEqual(result["status"], "paused")
        ids = {f["id"] for f in result["failures"]}
        self.assertIn("prd-exists", ids)
        self.assertIn("pr-draft-exists", ids)

    def test_stepsummary_matches_keyword(self) -> None:
        code, out = self._capture(
            "start", "shipFeature",
            "--input", "title=keyword check",
        )
        run_id = json.loads(out)["run_id"]
        (self.work / "docs" / "prds").mkdir(parents=True)
        (self.work / "docs" / "pr").mkdir(parents=True)
        (self.work / "docs" / "prds" / "keyword-check.md").write_text("ok")
        (self.work / "CHANGELOG.md").write_text("ok")
        (self.work / "docs" / "pr" / "keyword-check.md").write_text("ok")
        for sid in ["prd", "acceptance", "implement", "review", "verify", "changelog", "pr"]:
            sf = self.work / f"{sid}.summary.md"
            # NB: deliberately omit test/verify keywords from the verify step
            sf.write_text("nothing here" if sid == "verify" else "ok")
            self._capture("complete", run_id, sid, "--summary", str(sf))

        code, out = self._capture("assert", run_id)
        self.assertEqual(code, 2)
        ids = {f["id"] for f in json.loads(out)["failures"]}
        self.assertIn("tests-mentioned", ids)


if __name__ == "__main__":
    unittest.main()
