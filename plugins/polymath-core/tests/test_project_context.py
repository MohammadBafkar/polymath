"""Unit tests for polymath-core/hooks/scripts/load-project-context.py.

Covers:
  - YAML subset parser fallback (PyYAML present or absent — both should work)
  - Validation rejects: missing/wrong schemaVersion,
    bad commit_style/branch_strategy enums, malformed stack.languages,
    external_skills missing source, malformed setup / polymath activation keys.
  - Unknown top-level keys are warned and dropped, never fatal.
  - KNOWN_TOP_KEYS stays in sync with registry/schemas/project.schema.json
    (drift gate for the hand-written pair).
  - Resolution order: project → CLAUDE_CONFIG_DIR → home (first hit wins).
  - Machine-local overlay (.polymath/project.local.yaml): deep-merged above
    the winning file; fail-open on parse/validation problems; may serve as
    the sole source when no base file exists.
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

    def test_unknown_top_level_key_is_not_a_validation_error(self) -> None:
        errs = self.mod._validate({"schemaVersion": 1, "bogus": True})
        self.assertEqual(errs, [])

    def test_split_unknown_drops_and_reports(self) -> None:
        clean, dropped = self.mod._split_unknown(
            {"schemaVersion": 1, "bogus": True, "zz_later_key": {}}
        )
        self.assertEqual(dropped, ["bogus", "zz_later_key"])
        self.assertEqual(set(clean.keys()), {"schemaVersion"})

    def test_split_unknown_no_op_on_clean_input(self) -> None:
        data = {"schemaVersion": 1, "project": {"name": "x"}}
        clean, dropped = self.mod._split_unknown(data)
        self.assertEqual(dropped, [])
        self.assertIs(clean, data)

    def test_known_top_keys_match_schema_properties(self) -> None:
        schema = json.loads(
            (REPO_ROOT / "registry" / "schemas" / "project.schema.json").read_text()
        )
        self.assertEqual(
            self.mod.KNOWN_TOP_KEYS,
            set(schema["properties"].keys()),
            "loader KNOWN_TOP_KEYS drifted from project.schema.json properties",
        )

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

    def test_setup_required_tools_require_name(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "setup": {"required_tools": [{"check": "x --version"}]}}
        )
        self.assertTrue(any("setup.required_tools[0]" in e for e in errs))

    def test_polymath_recommended_plugins_require_name(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "polymath": {"recommended_plugins": [{"required": True}]}}
        )
        self.assertTrue(any("polymath.recommended_plugins[0]" in e for e in errs))

    def test_routing_mode_enum(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "routing": {"mode": "autopilot"}}
        )
        self.assertTrue(any("routing.mode" in e for e in errs))

    def test_routing_valid_modes_accepted(self) -> None:
        for mode in ("hint", "classify", "enforce"):
            errs = self.mod._validate({"schemaVersion": 1, "routing": {"mode": mode}})
            self.assertEqual(errs, [], f"mode {mode} should validate")

    def test_smoke_recipe_requires_start(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "smoke": {"python": {"port": 8000}}}
        )
        self.assertTrue(any("smoke.python missing `start`" in e for e in errs))

    def test_artifact_matrix_must_be_string(self) -> None:
        errs = self.mod._validate(
            {"schemaVersion": 1, "artifact_matrix": ["docs/matrix.md"]}
        )
        self.assertTrue(any("artifact_matrix" in e for e in errs))

    def test_new_mapping_keys_reject_non_mappings(self) -> None:
        for key in ("conventions_docs", "smoke", "tracker", "routing", "attribution"):
            errs = self.mod._validate({"schemaVersion": 1, key: ["not", "a", "map"]})
            self.assertTrue(
                any(f"{key} must be a mapping" in e for e in errs), key
            )

    def test_localization_keys_happy_path(self) -> None:
        errs = self.mod._validate(
            {
                "schemaVersion": 1,
                "conventions_docs": {
                    "backend-stack": "docs/conventions/backend.md",
                    "review-checklist": "docs/QUALITY.md",
                },
                "smoke": {
                    "python": {
                        "start": "uvicorn app:app",
                        "readiness": "/health",
                        "port": 8000,
                        "timeout_seconds": 60,
                    }
                },
                "tracker": {
                    "project": "My Project",
                    "work_item_types": {"bug": "Bug", "backlog": "Task"},
                    "marking": {"title_prefix": "[Agent]", "tag": "agent-created"},
                },
                "routing": {"mode": "hint"},
                "attribution": {"chat_markers": True, "commit_trailer": "Co-Authored-By: Bot <bot@example.com>"},
                "artifact_matrix": "docs/conventions/artifact-matrix.md",
                "prompts": {"plan_template": "docs/plan-template.md"},
            }
        )
        self.assertEqual(errs, [])

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
                "setup": {
                    "context_sources": ["README.md", "AGENTS.md"],
                    "required_tools": [{"name": "python3", "check": "python3 --version"}],
                    "environment": [{"name": "ANTHROPIC_API_KEY", "sensitive": True}],
                    "first_steps": ["Run validation"],
                },
                "polymath": {
                    "recommended_plugins": [{"name": "polymath-core", "required": True}],
                    "recommended_workflows": ["activateProject"],
                    "compatible_agents": ["claude-code", "codex"],
                },
            }
        )
        self.assertEqual(errs, [])


class DeepMergeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_loader()

    def test_mappings_merge_per_key_overlay_wins(self) -> None:
        merged = self.mod._deep_merge(
            {"project": {"name": "a", "description": "keep"}},
            {"project": {"name": "b"}},
        )
        self.assertEqual(merged["project"], {"name": "b", "description": "keep"})

    def test_lists_are_replaced_not_appended(self) -> None:
        merged = self.mod._deep_merge(
            {"stack": {"languages": [{"lang": "python"}]}},
            {"stack": {"languages": [{"lang": "go"}]}},
        )
        self.assertEqual(merged["stack"]["languages"], [{"lang": "go"}])

    def test_scalars_are_replaced(self) -> None:
        merged = self.mod._deep_merge(
            {"conventions": {"commit_style": "free-form"}},
            {"conventions": {"commit_style": "conventional-commits"}},
        )
        self.assertEqual(
            merged["conventions"]["commit_style"], "conventional-commits"
        )

    def test_new_keys_are_added(self) -> None:
        merged = self.mod._deep_merge(
            {"schemaVersion": 1},
            {"prompts": {"adr_template": "docs/adr-template.md"}},
        )
        self.assertEqual(merged["schemaVersion"], 1)
        self.assertEqual(merged["prompts"]["adr_template"], "docs/adr-template.md")

    def test_base_is_not_mutated(self) -> None:
        base = {"project": {"name": "a"}}
        self.mod._deep_merge(base, {"project": {"name": "b"}})
        self.assertEqual(base["project"]["name"], "a")


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

    def test_setup_and_recommended_plugins_listed(self) -> None:
        line = self.mod._summary_line(
            {
                "setup": {
                    "required_tools": [{"name": "python3"}],
                    "environment": [{"name": "ANTHROPIC_API_KEY"}],
                },
                "polymath": {
                    "recommended_plugins": [
                        {"name": "polymath-core"},
                        {"name": "polymath-flows"},
                    ]
                },
            }
        )
        self.assertIn("Setup: 1 tool(s), 1 env var(s)", line)
        self.assertIn("Recommended plugins: polymath-core, polymath-flows", line)


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
            "setup:\n"
            "  required_tools:\n"
            "    - name: python3\n"
            "      check: python3 --version\n"
            "  environment:\n"
            "    - name: ANTHROPIC_API_KEY\n"
            "      sensitive: true\n"
            "polymath:\n"
            "  recommended_plugins:\n"
            "    - name: polymath-core\n"
            "      required: true\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0, msg=cp.stderr)
        self.assertIn("Polymath: project context loaded", cp.stdout)
        self.assertIn("python 3.12 (fastapi)", cp.stdout)
        self.assertIn("Setup: 1 tool(s), 1 env var(s)", cp.stdout)
        self.assertIn("Recommended plugins: polymath-core", cp.stdout)
        out = json.loads(
            (self.data / "polymath-core" / "project-context.json").read_text()
        )
        self.assertEqual(out["project"]["name"], "demo")
        self.assertEqual(out["stack"]["languages"][0]["lang"], "python")
        self.assertEqual(out["setup"]["required_tools"][0]["name"], "python3")
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

    def test_unknown_top_key_warns_and_is_dropped_from_snapshot(self) -> None:
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\n"
            "project:\n"
            "  name: demo\n"
            "zz_future_key:\n"
            "  anything: true\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0, msg=cp.stderr)
        self.assertIn("ignoring unknown top-level key(s): zz_future_key", cp.stderr)
        out = json.loads(
            (self.data / "polymath-core" / "project-context.json").read_text()
        )
        self.assertNotIn("zz_future_key", out)
        self.assertEqual(out["_meta"]["ignored_keys"], ["zz_future_key"])

    def test_local_overlay_merges_above_project_file(self) -> None:
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\n"
            "project:\n"
            "  name: demo\n"
            "  description: team description\n"
            "stack:\n"
            "  languages:\n"
            "    - lang: python\n"
            "conventions:\n"
            "  commit_style: conventional-commits\n"
        )
        (self.work / ".polymath" / "project.local.yaml").write_text(
            "conventions:\n"
            "  commit_style: free-form\n"
            "prompts:\n"
            "  adr_template: docs/my-adr.md\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0, msg=cp.stderr)
        out = json.loads(
            (self.data / "polymath-core" / "project-context.json").read_text()
        )
        # Overlay leaf wins; untouched base keys survive; new keys are added.
        self.assertEqual(out["conventions"]["commit_style"], "free-form")
        self.assertEqual(out["project"]["description"], "team description")
        self.assertEqual(out["prompts"]["adr_template"], "docs/my-adr.md")
        self.assertTrue(out["_meta"]["source"].endswith("project.yaml"))
        self.assertTrue(out["_meta"]["overlay"].endswith("project.local.yaml"))

    def test_invalid_overlay_is_skipped_fail_open(self) -> None:
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\n"
            "project:\n"
            "  name: demo\n"
        )
        (self.work / ".polymath" / "project.local.yaml").write_text(
            "conventions:\n"
            "  commit_style: not-a-real-style\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0, msg=cp.stderr)
        self.assertIn("ignoring overlay", cp.stderr)
        out = json.loads(
            (self.data / "polymath-core" / "project-context.json").read_text()
        )
        self.assertNotIn("conventions", out)
        self.assertNotIn("overlay", out["_meta"])

    def test_overlay_alone_serves_as_source(self) -> None:
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.local.yaml").write_text(
            "schemaVersion: 1\n"
            "stack:\n"
            "  languages:\n"
            "    - lang: rust\n"
        )
        cp = self._run()
        self.assertEqual(cp.returncode, 0, msg=cp.stderr)
        self.assertIn("rust", cp.stdout)
        out = json.loads(
            (self.data / "polymath-core" / "project-context.json").read_text()
        )
        self.assertTrue(out["_meta"]["source"].endswith("project.local.yaml"))
        self.assertNotIn("overlay", out["_meta"])

    def test_invalid_overlay_alone_clears_snapshot_quietly(self) -> None:
        (self.data / "polymath-core").mkdir(parents=True)
        (self.data / "polymath-core" / "project-context.json").write_text(
            '{"old": true}'
        )
        (self.work / ".polymath").mkdir()
        (self.work / ".polymath" / "project.local.yaml").write_text(
            "conventions:\n"
            "  commit_style: nope\n"
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
