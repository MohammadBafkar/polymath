"""Unit tests for build-time `extends` flattening in bin/polymath-flow.

Covers:
  - partial validation (_validate_partial)
  - merge semantics (_flatten): override-by-id, insertAfter ordering, step
    append, mustPass/guards append, scalar replacement, name/version
    inheritance, version-pin prefix match
  - provenance stamping + deterministic hash
  - the flatten CLI: --out, --check fresh/stale/missing
  - the runtime hard-error on extends/override/insertAfter (validate, and
    the next/assert reload guard)
  - schema↔runner mirror drift gates (ALLOWED_TOP_LEVEL / ALLOWED_CHECK_TYPES
    vs registry/schemas/workflow.schema.json)

Run with: python3 -m unittest discover -s plugins/polymath-flows/tests
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
SCHEMA_PATH = REPO_ROOT / "registry" / "schemas" / "workflow.schema.json"


def _import_flow():
    loader = importlib.machinery.SourceFileLoader("polymath_flow_flat", str(FLOW_SCRIPT))
    spec = importlib.util.spec_from_loader("polymath_flow_flat", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _parent() -> dict:
    return {
        "schemaVersion": 0.1,
        "name": "parentFlow",
        "version": "0.1.3",
        "description": "Parent under test.",
        "whenToUse": "Exercise flattening in unit tests.",
        "steps": [
            {"id": "one", "invoke": "a:b", "prompt": "First."},
            {"id": "two", "invoke": "a:c", "prompt": "Second."},
            {"id": "three", "invoke": "a:d", "prompt": "Third."},
        ],
        "mustPass": [
            {"id": "smoke", "type": "commandSucceeds", "command": "true"},
        ],
    }


REF = "polymath-flows:parentFlow@0.1"


class ValidatePartialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_minimal_partial_ok(self) -> None:
        errs = self.mod._validate_partial(
            {"schemaVersion": 0.1, "extends": REF, "mustPass": []}
        )
        self.assertEqual(errs, [])

    def test_missing_extends_rejected(self) -> None:
        errs = self.mod._validate_partial({"schemaVersion": 0.1, "mustPass": []})
        self.assertTrue(any("extends must be" in e for e in errs))

    def test_contributes_nothing_rejected(self) -> None:
        errs = self.mod._validate_partial({"schemaVersion": 0.1, "extends": REF})
        self.assertTrue(any("contributes nothing" in e for e in errs))

    def test_provenance_in_partial_rejected(self) -> None:
        errs = self.mod._validate_partial(
            {
                "schemaVersion": 0.1,
                "extends": REF,
                "mustPass": [],
                "provenance": {"extends": REF, "hash": "sha256:" + "0" * 64},
            }
        )
        self.assertTrue(any("stamped by flatten" in e for e in errs))


class FlattenMergeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_override_replaces_by_id(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "override": {
                "steps": [{"id": "two", "invoke": "x:y", "prompt": "Replaced."}]
            },
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertEqual(errs, [])
        self.assertEqual([s["id"] for s in flat["steps"]], ["one", "two", "three"])
        self.assertEqual(flat["steps"][1]["invoke"], "x:y")

    def test_override_unknown_id_rejected(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "override": {"steps": [{"id": "nope", "invoke": "x:y", "prompt": "?"}]},
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertIsNone(flat)
        self.assertTrue(any("does not exist in the parent" in e for e in errs))

    def test_insert_after_preserves_order(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "insertAfter": {
                "one": [
                    {"id": "one-a", "invoke": "x:a", "prompt": "A."},
                    {"id": "one-b", "invoke": "x:b", "prompt": "B."},
                ]
            },
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertEqual(errs, [])
        self.assertEqual(
            [s["id"] for s in flat["steps"]],
            ["one", "one-a", "one-b", "two", "three"],
        )

    def test_insert_after_unknown_anchor_rejected(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "insertAfter": {"missing": [{"id": "n", "invoke": "x:a", "prompt": "A."}]},
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertIsNone(flat)
        self.assertTrue(any("anchor" in e for e in errs))

    def test_insert_colliding_id_rejected(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "insertAfter": {"one": [{"id": "two", "invoke": "x:a", "prompt": "A."}]},
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertIsNone(flat)
        self.assertTrue(any("collides" in e for e in errs))

    def test_partial_steps_append(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "steps": [{"id": "tail", "invoke": "x:t", "prompt": "Tail."}],
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertEqual(errs, [])
        self.assertEqual(flat["steps"][-1]["id"], "tail")

    def test_mustpass_and_guards_append(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "mustPass": [{"id": "extra", "type": "fileExists", "path": "x"}],
            "guards": [{"id": "pre", "type": "command", "command": "true"}],
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertEqual(errs, [])
        self.assertEqual([c["id"] for c in flat["mustPass"]], ["smoke", "extra"])
        self.assertEqual([c["id"] for c in flat["guards"]], ["pre"])

    def test_scalars_replace_and_name_inherits(self) -> None:
        partial = {
            "schemaVersion": 0.1,
            "extends": REF,
            "description": "Localized.",
            "mustPass": [],
        }
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertEqual(errs, [])
        self.assertEqual(flat["name"], "parentFlow")  # inherited
        self.assertEqual(flat["version"], "0.1.3")  # inherited
        self.assertEqual(flat["description"], "Localized.")  # replaced

    def test_version_pin_prefix_mismatch_rejected(self) -> None:
        ref = "polymath-flows:parentFlow@0.2"
        partial = {"schemaVersion": 0.1, "extends": ref, "mustPass": []}
        flat, errs = self.mod._flatten(partial, _parent(), ref)
        self.assertIsNone(flat)
        self.assertTrue(any("pins @0.2" in e for e in errs))

    def test_provenance_stamped_and_hash_deterministic(self) -> None:
        partial = {"schemaVersion": 0.1, "extends": REF, "mustPass": []}
        flat1, _ = self.mod._flatten(partial, _parent(), REF)
        flat2, _ = self.mod._flatten(partial, _parent(), REF)
        prov = flat1["provenance"]
        self.assertEqual(prov["extends"], REF)
        self.assertEqual(prov["parentVersion"], "0.1.3")
        self.assertRegex(prov["hash"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(flat1, flat2)
        # Different sources hash differently.
        other = dict(partial, description="changed")
        flat3, _ = self.mod._flatten(other, _parent(), REF)
        self.assertNotEqual(prov["hash"], flat3["provenance"]["hash"])

    def test_build_time_keys_stripped_and_result_validates(self) -> None:
        partial = {"schemaVersion": 0.1, "extends": REF, "mustPass": []}
        flat, errs = self.mod._flatten(partial, _parent(), REF)
        self.assertEqual(errs, [])
        for key in ("extends", "override", "insertAfter"):
            self.assertNotIn(key, flat)
        self.assertEqual(self.mod._validate(flat), [])


class RuntimeHardErrorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_flow()

    def test_validate_rejects_each_build_time_key(self) -> None:
        for key, value in (
            ("extends", REF),
            ("override", {"steps": []}),
            ("insertAfter", {"one": []}),
        ):
            wf = {
                "schemaVersion": 0.1,
                "name": "x",
                "version": "1.0.0",
                "steps": [{"id": "s", "invoke": "a:b", "prompt": "p"}],
                key: value,
            }
            errs = self.mod._validate(wf)
            self.assertTrue(
                any("build-time only" in e for e in errs),
                f"{key} did not hard-error: {errs}",
            )

    def test_provenance_validates_shape(self) -> None:
        wf = {
            "schemaVersion": 0.1,
            "name": "x",
            "version": "1.0.0",
            "steps": [{"id": "s", "invoke": "a:b", "prompt": "p"}],
            "provenance": {"extends": "bad ref", "hash": "nope"},
        }
        errs = self.mod._validate(wf)
        self.assertTrue(any("provenance.extends" in e for e in errs))
        self.assertTrue(any("provenance.hash" in e for e in errs))


class FlattenCliTests(unittest.TestCase):
    """Drive the flatten CLI against the real catalog shipFeature parent."""

    PARTIAL = (
        "schemaVersion: 0.1\n"
        "extends: polymath-flows:shipFeature@0.1\n"
        "insertAfter:\n"
        "  implement:\n"
        "    - id: license-check\n"
        "      invoke: polymath-release:pr\n"
        "      prompt: Check third-party dependency changes.\n"
    )

    def setUp(self) -> None:
        self.mod = _import_flow()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)

    def tearDown(self) -> None:
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

    def test_flatten_out_check_and_drift(self) -> None:
        partial = self.work / "partial.yaml"
        flattened = self.work / "flattened.yaml"
        partial.write_text(self.PARTIAL)

        code, out = self._capture("flatten", str(partial), "--out", str(flattened))
        self.assertEqual(code, 0, out)
        payload = json.loads(out)
        self.assertTrue(flattened.exists())
        self.assertRegex(payload["provenance"]["hash"], r"^sha256:[0-9a-f]{64}$")

        # The flattened output is a runnable workflow.
        code, _ = self._capture("validate", str(flattened))
        self.assertEqual(code, 0)

        # Fresh --check passes.
        code, _ = self._capture("flatten", str(partial), "--out", str(flattened), "--check")
        self.assertEqual(code, 0)

        # Editing the partial makes --check report drift (exit 1).
        partial.write_text(self.PARTIAL.replace("third-party", "3rd-party"))
        code, _ = self._capture("flatten", str(partial), "--out", str(flattened), "--check")
        self.assertEqual(code, 1)

    def test_check_missing_out_is_drift(self) -> None:
        partial = self.work / "partial.yaml"
        partial.write_text(self.PARTIAL)
        code, _ = self._capture(
            "flatten", str(partial), "--out", str(self.work / "absent.yaml"), "--check"
        )
        self.assertEqual(code, 1)

    def test_unknown_parent_is_not_found(self) -> None:
        partial = self.work / "partial.yaml"
        partial.write_text(
            "schemaVersion: 0.1\nextends: polymath-flows:noSuchFlow@0.1\nmustPass: []\n"
        )
        code, _ = self._capture("flatten", str(partial), "--out", str(self.work / "o.yaml"))
        self.assertEqual(code, 3)

    def test_next_refuses_source_that_gained_extends(self) -> None:
        """A run whose source file gains `extends` after start must refuse
        to continue (next re-reads the YAML without re-validating)."""
        prev_cwd = pathlib.Path.cwd()
        prev_data = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.work / ".pdata")
        os.chdir(self.work)
        try:
            wf_dir = self.work / ".claude" / "polymath" / "workflows"
            wf_dir.mkdir(parents=True)
            source = wf_dir / "tinyFlow.yaml"
            source.write_text(
                "schemaVersion: 0.1\n"
                "name: tinyFlow\n"
                "version: 0.1.0\n"
                "steps:\n"
                "  - id: only\n"
                "    invoke: a:b\n"
                "    prompt: Do the thing.\n"
            )
            code, out = self._capture("start", "tinyFlow")
            self.assertEqual(code, 0, out)
            run_id = json.loads(out)["run_id"]
            source.write_text(
                "schemaVersion: 0.1\n"
                "extends: polymath-flows:shipFeature@0.1\n"
                "mustPass: []\n"
            )
            code, _ = self._capture("next", run_id)
            self.assertEqual(code, 2)
        finally:
            os.chdir(prev_cwd)
            if prev_data is None:
                os.environ.pop("CLAUDE_PLUGIN_DATA", None)
            else:
                os.environ["CLAUDE_PLUGIN_DATA"] = prev_data


class SchemaMirrorDriftTests(unittest.TestCase):
    """The runner's hand-rolled validator mirrors registry/schemas/
    workflow.schema.json. These gates fail when one side moves alone —
    the workflow-schema analogue of the Phase 0 KNOWN_TOP_KEYS gate."""

    def setUp(self) -> None:
        self.mod = _import_flow()
        self.schema = json.loads(SCHEMA_PATH.read_text())

    def test_top_level_keys_match_schema_properties(self) -> None:
        self.assertEqual(
            set(self.schema["properties"].keys()), self.mod.ALLOWED_TOP_LEVEL
        )

    def test_check_types_match_schema_enum(self) -> None:
        enum = set(
            self.schema["$defs"]["check"]["properties"]["type"]["enum"]
        )
        self.assertEqual(enum, self.mod.ALLOWED_CHECK_TYPES)

    def test_strong_and_advisory_sets_are_known_types(self) -> None:
        self.assertTrue(self.mod.STRONG_CHECK_TYPES <= self.mod.ALLOWED_CHECK_TYPES)
        self.assertTrue(self.mod.ADVISORY_BY_DEFAULT <= self.mod.ALLOWED_CHECK_TYPES)


if __name__ == "__main__":
    unittest.main()
