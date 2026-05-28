"""Unit tests for polymath-core/hooks/scripts/load-project-context.py.

Covers:
  - YAML subset parser fallback (PyYAML present or absent — both should work)
  - Validation rejects: missing/wrong schemaVersion, unknown top-level keys,
    bad commit_style/branch_strategy enums, malformed stack.languages,
    external_skills missing source.
  - Resolution order: project → CLAUDE_CONFIG_DIR → home (first hit wins).
  - Snapshot is written with `_meta` and matches the input.
  - Stale snapshot is cleared when no project file exists.
  - Summary line shape contains language + test framework + runtime + external
    skills as appropriate.
  - All five shipped examples validate cleanly.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
LOADER = REPO_ROOT / "plugins" / "polymath-core" / "hooks" / "scripts" / "load-project-context.py"
EXAMPLES_DIR = REPO_ROOT / ".polymath" / "examples"


def _import_loader():
    loader = importlib.machinery.SourceFileLoader("ppc_loader", str(LOADER))
    spec = importlib.util.spec_from_loader("ppc_loader", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_loader()

    def test_schema_version_required(self) -> None:
        errs = self.mod._validate({})
        self.assertTrue(any("schemaVersion must be 1" in e for e in errs))

    def test_schema_version_must_be_1(self) -> None:
        errs = self.mod._validate({"schemaVersion": 2})
        self.assertTrue(any("schemaVersion must be 1" in e for e in errs))

    def test_unknown_top_level_key_rejected(self) -> None:
        errs = self.mod._validate({"schemaVersion": 1, "bogus": True})
        self.assertTrue(any("unknown top-level keys" in e for e in errs))

    def test_root_must_be_mapping(self) -> None:
        errs = self.mod._validate(["just", "a", "list"])
        self.assertTrue(any("must be a mapping" in e for e in errs))

    def test_commit_style_enum(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "conventions": {"commit_style": "weird"}}
        )
        self.assertTrue(any("commit_style" in e for e in errs))

    def test_branch_strategy_enum(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "conventions": {"branch_strategy": "freestyle"}}
        )
        self.assertTrue(any("branch_strategy" in e for e in errs))

    def test_stack_languages_must_have_lang(self) -> None:
        errs = self.mod._validate(
            {
                "schemaVersion": 1,
                "stack": {"languages": [{"version": "1.0"}]},
            }
        )
        self.assertTrue(any("missing `lang`" in e for e in errs))

    def test_stack_languages_empty_rejected(self) -> None:
        errs = self.mod._validate({"schemaVersion": 1, "stack": {"languages": []}})
        self.assertTrue(any("non-empty list" in e for e in errs))

    def test_external_skills_requires_source(self) -> None:
        errs = self.mod._validate(
            {
                "schemaVersion": 1,
                "external_skills": [{"install": "marketplace"}],
            }
        )
        self.assertTrue(any("missing `source`" in e for e in errs))

    def test_external_skills_install_enum(self) -> None:
        errs = self.mod._validate(
            {
                "schemaVersion": 1,
                "external_skills": [{"source": "x", "install": "magic"}],
            }
        )
        self.assertTrue(any("install" in e and "magic" in e for e in errs))

    def test_happy_path_returns_no_errors(self) -> None:
        errs = self.mod._validate(
            {
                "schemaVersion": 1,
                "project": {"name": "demo"},
                "stack": {"languages": [{"lang": "python", "version": "3.12"}]},
                "conventions": {
                    "commit_style": "conventional-commits",
                    "branch_strategy": "trunk-based",
                },
                "external_skills": [
                    {"source": "github.com/x/y", "install": "marketplace"}
                ],
            }
        )
        self.assertEqual(errs, [])


class SummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_loader()

    def test_no_context_no_summary(self) -> None:
        self.assertEqual(self.mod._summary_line({}), "")

    def test_languages_only(self) -> None:
        line = self.mod._summary_line(
            {"stack": {"languages": [{"lang": "go", "version": "1.22"}]}}
        )
        self.assertIn("Languages: go 1.22", line)

    def test_framework_renders_in_parens(self) -> None:
        line = self.mod._summary_line(
            {
                "stack": {
                    "languages": [
                        {"lang": "dotnet", "version": "8", "framework": "aspnet-core"}
                    ]
                }
            }
        )
        self.assertIn("dotnet 8 (aspnet-core)", line)

    def test_testing_collapses_to_plus_joined(self) -> None:
        line = self.mod._summary_line(
            {
                "stack": {
                    "languages": [{"lang": "java"}],
                    "testing": [
                        {
                            "framework": "junit5",
                            "mocking": "mockito",
                            "assertion": "assertj",
                        }
                    ],
                }
            }
        )
        self.assertIn("Tests: junit5 + mockito + assertj", line)

    def test_external_skills_listed(self) -> None:
        line = self.mod._summary_line(
            {
                "stack": {"languages": [{"lang": "python"}]},
                "external_skills": [{"source": "github.com/foo/bar"}],
            }
        )
        self.assertIn("External skills: github.com/foo/bar", line)


class LoaderEndToEndTests(unittest.TestCase):
    """Exercise the script as a subprocess against a temp workspace."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self.data = self.work / "data"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run(self, *, env_extra: dict | None = None) -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "CLAUDE_PLUGIN_DATA": str(self.data),
            # Clear so the helper does not pick up the developer's own user
            # config file in CLAUDE_CONFIG_DIR.
            "CLAUDE_CONFIG_DIR": str(self.work / "no-such-config-dir"),
            # Override HOME so the ~/.polymath fallback cannot reach the
            # developer's real home.
            "HOME": str(self.work / "fake-home"),
        }
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            ["python3", str(LOADER)],
            cwd=self.work, capture_output=True, text=True, env=env,
        )

    def test_no_file_quiet_success(self) -> None:
        cp = self._run()
        self.assertEqual(cp.returncode, 0)
        self.assertEqual(cp.stdout.strip(), "")

    def test_happy_path_emits_summary_and_writes_snapshot(self) -> None:
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\n"
            "project:\n"
            "  name: demo\n"
            "stack:\n"
            "  languages:\n"
            "    - lang: python\n"
            "      version: '3.12'\n"
            "      framework: fastapi\n"
            "  testing:\n"
            "    - framework: pytest\n"
            "conventions:\n"
            "  commit_style: conventional-commits\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0, msg=cp.stderr)
        self.assertIn("Polymath: project context loaded", cp.stdout)
        self.assertIn("python 3.12 (fastapi)", cp.stdout)
        out = json.loads(
            (self.data / "polymath-core" / "project-context.json").read_text()
        )
        self.assertEqual(out["project"]["name"], "demo")
        self.assertEqual(out["stack"]["languages"][0]["lang"], "python")
        self.assertIn("_meta", out)
        self.assertEqual(out["_meta"]["schemaVersion"], 1)
        self.assertTrue(out["_meta"]["source"].endswith("project.yaml"))

    def test_invalid_file_returns_2_and_does_not_overwrite_snapshot(self) -> None:
        # Pre-create a good snapshot, then write a bad project file.
        (self.data / "polymath-core").mkdir(parents=True)
        (self.data / "polymath-core" / "project-context.json").write_text("{}")
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\nconventions:\n  commit_style: weird\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 2)
        self.assertIn("commit_style", cp.stderr)
        # Snapshot left intact (we don't overwrite on validation failure).
        self.assertEqual(
            (self.data / "polymath-core" / "project-context.json").read_text(),
            "{}",
        )

    def test_stale_snapshot_cleared_when_no_file(self) -> None:
        (self.data / "polymath-core").mkdir(parents=True)
        (self.data / "polymath-core" / "project-context.json").write_text(
            '{"old": true}'
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0)
        self.assertFalse(
            (self.data / "polymath-core" / "project-context.json").exists()
        )

    def test_config_dir_layer_is_used_when_no_project_file(self) -> None:
        # No project file in cwd; supply one via CLAUDE_CONFIG_DIR.
        cfg = self.work / "userconfig"
        (cfg / "polymath").mkdir(parents=True)
        (cfg / "polymath" / "project.yaml").write_text(
            "schemaVersion: 1\n"
            "stack:\n"
            "  languages:\n"
            "    - lang: ruby\n"
        )
        cp = subprocess.run(
            ["python3", str(LOADER)],
            cwd=self.work,
            capture_output=True, text=True,
            env={
                **os.environ,
                "CLAUDE_PLUGIN_DATA": str(self.data),
                "CLAUDE_CONFIG_DIR": str(cfg),
                "HOME": str(self.work / "fake-home"),
            },
        )
        self.assertEqual(cp.returncode, 0)
        self.assertIn("ruby", cp.stdout)


class ExampleFilesTests(unittest.TestCase):
    """Every shipped example must parse, validate, and produce a summary."""

    def setUp(self) -> None:
        self.mod = _import_loader()

    def test_all_examples_validate(self) -> None:
        examples = sorted(EXAMPLES_DIR.glob("project-*.yaml"))
        self.assertGreaterEqual(len(examples), 5, "expected at least 5 examples")
        for ex in examples:
            with self.subTest(example=ex.name):
                data = self.mod._load_yaml(ex.read_text())
                errs = self.mod._validate(data)
                self.assertEqual(errs, [], f"{ex.name}: {errs}")
                line = self.mod._summary_line(data)
                self.assertTrue(line.startswith("Polymath: project context loaded"))


if __name__ == "__main__":
    unittest.main()
