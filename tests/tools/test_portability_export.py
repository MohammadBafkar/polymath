"""Tests for tools/export-agents-skills.py portable bundle generation."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTER = REPO_ROOT / "tools" / "export-agents-skills.py"


class PortableExportTests(unittest.TestCase):
    def test_bundle_exports_all_portable_surface_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "bundle"
            cp = subprocess.run(
                ["python3", str(EXPORTER), "--out", str(out)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(cp.returncode, 0, cp.stderr + cp.stdout)

            manifest = json.loads((out / "manifest.json").read_text())
            expected_skills = len(list((REPO_ROOT / "plugins").glob("*/skills/*/SKILL.md")))
            expected_commands = len(list((REPO_ROOT / "plugins").glob("*/commands/*.md")))
            expected_agents = len(
                [p for p in (REPO_ROOT / "plugins").glob("*/agents/*.md")]
            )
            expected_hooks = len(list((REPO_ROOT / "plugins").glob("*/hooks/hooks.json")))
            expected_templates = len(
                [
                    p
                    for p in (REPO_ROOT / "plugins").glob("*/templates/**/*")
                    if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
                ]
            )

            self.assertEqual(manifest["skillCount"], expected_skills)
            self.assertEqual(manifest["commandCount"], expected_commands)
            self.assertEqual(manifest["agentCount"], expected_agents)
            self.assertEqual(manifest["hookCount"], expected_hooks)
            self.assertEqual(manifest["templateCount"], expected_templates)
            self.assertEqual(
                manifest["discoverableSkillCount"],
                expected_skills + expected_commands + expected_agents,
            )
            self.assertIn("paths", manifest)
            self.assertEqual(manifest["paths"]["dataRoot"]["default"], "~/.polymath/data")
            self.assertTrue((out / "_polymath" / "mcp" / "mcp.json").is_file())

    def test_every_exported_skill_has_a_valid_frontmatter_fence(self) -> None:
        # Commands whose source frontmatter carries only a description (no
        # name) must still export a well-formed `---\nname: ...` fence, not a
        # glued `---name:` that breaks agentskills.io parsing.
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "bundle"
            cp = subprocess.run(
                ["python3", str(EXPORTER), "--out", str(out)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(cp.returncode, 0, cp.stderr + cp.stdout)

            for skill_md in out.glob("*/SKILL.md"):
                text = skill_md.read_text()
                self.assertTrue(
                    text.startswith("---\n"),
                    f"{skill_md} does not open with a `---` fence on its own line",
                )
                fm = text.split("\n---", 1)[0]
                self.assertRegex(
                    fm, r"(?m)^name:\s*\S", f"{skill_md} frontmatter has no name"
                )

    def test_bundle_is_self_contained_and_host_loadable(self) -> None:
        # Every relative/`_polymath` reference in an exported skill must resolve
        # to a real file in the bundle; the exporter's host-load verifier (run
        # as part of --check) fails closed otherwise.
        cp = subprocess.run(
            ["python3", str(EXPORTER), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(cp.returncode, 0, cp.stderr + cp.stdout)
        self.assertIn("host-load verify:", cp.stdout)
        self.assertIn("0 dangling", cp.stdout)

    def test_bundle_ships_runnable_hook_dispatcher(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "bundle"
            subprocess.run(
                ["python3", str(EXPORTER), "--out", str(out)],
                cwd=REPO_ROOT, capture_output=True, text=True, check=True,
            )
            dispatcher = out / "_polymath" / "hooks" / "run-hook.py"
            self.assertTrue(dispatcher.is_file(), "missing hook dispatcher")
            # An event with no registered hook is a successful no-op.
            noop = subprocess.run(
                ["python3", str(dispatcher), "NoSuchEvent"],
                cwd=td, capture_output=True, text=True,
            )
            self.assertEqual(noop.returncode, 0, noop.stderr)
            # A registered SessionStart hook actually executes and does its work
            # via the portable POLYMATH_DATA_DIR (proven by its side-effect file).
            data = pathlib.Path(td) / "data"
            ran = subprocess.run(
                ["python3", str(dispatcher), "SessionStart"],
                cwd=td, capture_output=True, text=True,
                env={**os.environ, "POLYMATH_PROJECT_DIR": str(REPO_ROOT),
                     "POLYMATH_DATA_DIR": str(data)},
            )
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertTrue(
                any(data.rglob("*")) if data.exists() else False,
                "SessionStart dispatch produced no side effect under POLYMATH_DATA_DIR",
            )

    def test_install_deploys_and_verifies_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "build"
            target = pathlib.Path(td) / ".agents" / "skills"
            cp = subprocess.run(
                ["python3", str(EXPORTER), "--out", str(out), "--install", str(target)],
                cwd=REPO_ROOT, capture_output=True, text=True,
            )
            self.assertEqual(cp.returncode, 0, cp.stderr + cp.stdout)
            self.assertIn("installed:", cp.stdout)
            self.assertTrue((target / "manifest.json").is_file())
            self.assertTrue((target / "_polymath" / "hooks" / "run-hook.py").is_file())

    def test_exported_markdown_rewrites_claude_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "bundle"
            cp = subprocess.run(
                ["python3", str(EXPORTER), "--out", str(out)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(cp.returncode, 0, cp.stderr + cp.stdout)

            forbidden = (
                "CLAUDE_PLUGIN_ROOT",
                "CLAUDE_PLUGIN_DATA",
                "CLAUDE_CONFIG_DIR",
                "CLAUDE_PROJECT_DIR",
                "$HOME/.claude/plugins/data",
                "~/.claude/plugins/data",
            )
            for skill_md in out.glob("*/SKILL.md"):
                text = skill_md.read_text()
                for token in forbidden:
                    self.assertNotIn(token, text, skill_md)

            command = out / "polymath-author-command-new-plugin" / "SKILL.md"
            self.assertIn("../_polymath/support/polymath-author/bin/new-plugin.sh", command.read_text())
            hook = json.loads(
                (out / "_polymath" / "hooks" / "polymath-core.hooks.json").read_text()
            )
            commands = [event["command"] for event in hook["events"]]
            self.assertTrue(commands)
            self.assertTrue(all("${CLAUDE_PLUGIN_ROOT}" not in c for c in commands))
            self.assertTrue(any(c.startswith("../support/polymath-core/") for c in commands))


if __name__ == "__main__":
    unittest.main()
