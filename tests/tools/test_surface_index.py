"""Unit tests for tools/build-surface-index.py — routing schema v1.

Covers the declaration checks the SURFACE-INDEX gate relies on:
schemaVersion const, tier enum, events regex compilation, the
self-veto guard, the repo-probe cap, and the compiled events /
repo_probes / tier outputs.

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "build-surface-index.py"


def _import_builder():
    loader = importlib.machinery.SourceFileLoader("build_surface_index", str(SCRIPT))
    spec = importlib.util.spec_from_loader("build_surface_index", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SchemaV1ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _import_builder()
        cls.schema = cls.mod._load_schema()
        assert cls.schema is not None, "surface-routing.schema.json must load"

    def _errors(self, body: dict) -> list[str]:
        errors: list[str] = []
        self.mod._validate(body, self.schema, "test.yaml", errors)
        return errors

    def test_v1_keys_accepted(self) -> None:
        body = {
            "schemaVersion": 1,
            "tier": "hard",
            "regex": [r"\bACME-\d+\b"],
            "intents": ["deploy the service"],
            "not_intents": ["roll back"],
            "repo_state": ["Dockerfile", "*.tf"],
            "events": [
                {"command": r"\bdeploy\b", "output": r"FAILED", "why": "failed deploy", "note": "n"}
            ],
        }
        self.assertEqual(self._errors(body), [])

    def test_events_only_satisfies_signal_requirement(self) -> None:
        body = {"events": [{"command": r"\bpytest\b", "output": r"failed", "why": "w"}]}
        self.assertEqual(self._errors(body), [])

    def test_schema_version_other_than_1_rejected(self) -> None:
        self.assertTrue(self._errors({"schemaVersion": 2, "regex": ["x"]}))

    def test_bad_tier_rejected(self) -> None:
        self.assertTrue(self._errors({"tier": "diamond", "regex": ["x"]}))

    def test_event_missing_why_rejected(self) -> None:
        self.assertTrue(self._errors({"events": [{"command": "a", "output": "b"}]}))

    def test_event_regex_must_compile(self) -> None:
        errs = self._errors({"events": [{"command": "[unclosed", "output": "ok", "why": "w"}]})
        self.assertTrue(any("does not compile" in e for e in errs))

    def test_self_veto_rejected(self) -> None:
        errs = self._errors({
            "regex": ["x"],
            "intents": ["Deploy the thing"],
            "not_intents": ["deploy the thing"],
        })
        self.assertTrue(any("veto this surface's own intents" in e for e in errs))

    def test_unknown_key_rejected(self) -> None:
        self.assertTrue(self._errors({"regex": ["x"], "made_up_key": True}))


class CompileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _import_builder()

    def _decl(self, body: dict, ident: str = "demo") -> dict:
        return {"kind": "skill", "id": ident, "surface": f"demo:{ident}", "body": body, "where": "t"}

    def test_build_rule_carries_v1_keys(self) -> None:
        rule = self.mod.build_rule(self._decl({
            "regex": ["x"],
            "not_intents": ["nope"],
            "repo_state": ["*.tf"],
            "tier": "hard",
        }))
        self.assertEqual(rule["not_intents"], ["nope"])
        self.assertEqual(rule["repo_state"], ["*.tf"])
        self.assertEqual(rule["tier"], "hard")

    def test_soft_tier_not_carried_in_rule_but_indexed(self) -> None:
        decl = self._decl({"regex": ["x"], "tier": "soft"})
        self.assertNotIn("tier", self.mod.build_rule(decl))
        self.assertEqual(self.mod.build_index_entry(decl)["tier"], "soft")

    def test_events_compiled_with_surface(self) -> None:
        events = self.mod.build_events([self._decl({
            "events": [{"command": "c", "output": "o", "why": "w", "note": "n"}],
        })])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["surface"], "demo:demo")
        self.assertEqual(events[0]["note"], "n")

    def test_repo_probe_union_capped(self) -> None:
        decls = [
            self._decl({"regex": ["x"], "repo_state": [f"probe-{i}-{j}" for j in range(13)]}, f"s{i}")
            for i in range(5)
        ]  # 65 distinct probes
        probes, errors = self.mod.collect_repo_probes(decls)
        self.assertEqual(len(probes), 65)
        self.assertTrue(any("exceeds the 64-probe cap" in e for e in errors))

    def test_real_catalog_is_clean(self) -> None:
        decls, errors = self.mod.collect()
        errors += self.mod.collect_repo_probes(decls)[1]
        self.assertEqual(errors, [])
        self.assertTrue(any(d["id"] == "bugTriage" for d in decls))


if __name__ == "__main__":
    unittest.main()
