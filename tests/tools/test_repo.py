"""Unit tests for tools/lib/repo.py — run against the live tree.

Cheap structural assertions only: the helpers must agree with the
marketplace / catalog the same way check-registry.py catalog asserts they agree
with each other. No fixture tree; a plugin add/remove that updates the
catalogs keeps these green automatically.

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.lib.repo import (  # noqa: E402
    iter_plugins,
    iter_skills,
    load_catalog,
    load_marketplace,
    plugins_dir,
    repo_root,
)


class RepoRootTests(unittest.TestCase):
    def test_repo_root_is_this_checkout(self) -> None:
        self.assertEqual(repo_root(), REPO_ROOT)

    def test_repo_root_landmarks_exist(self) -> None:
        self.assertTrue((repo_root() / ".claude-plugin" / "marketplace.json").is_file())
        self.assertTrue((repo_root() / "registry" / "polymath-catalog.json").is_file())
        self.assertTrue(plugins_dir().is_dir())


class IterPluginsTests(unittest.TestCase):
    def test_plugin_count_matches_marketplace(self) -> None:
        plugins = list(iter_plugins())
        marketplace = load_marketplace()
        self.assertEqual(len(plugins), len(marketplace["plugins"]))

    def test_plugin_names_match_marketplace_and_catalog(self) -> None:
        names = {p.name for p in iter_plugins()}
        self.assertEqual(names, {e["name"] for e in load_marketplace()["plugins"]})
        self.assertEqual(names, set(load_catalog()["plugins"].keys()))

    def test_sorted_directories_only(self) -> None:
        plugins = list(iter_plugins())
        self.assertEqual([p.name for p in plugins], sorted(p.name for p in plugins))
        for p in plugins:
            self.assertTrue(p.is_dir())
            self.assertTrue((p / ".claude-plugin" / "plugin.json").is_file())


class IterSkillsTests(unittest.TestCase):
    def test_every_yielded_path_is_a_skill_md(self) -> None:
        skills = list(iter_skills())
        self.assertGreater(len(skills), 0)
        plugin_names = {p.name for p in iter_plugins()}
        for s in skills:
            self.assertEqual(s.name, "SKILL.md")
            self.assertTrue(s.is_file())
            self.assertIn(s.parents[2].name, plugin_names)

    def test_matches_a_direct_glob_of_the_tree(self) -> None:
        expected = sorted(plugins_dir().glob("*/skills/*/SKILL.md"))
        self.assertEqual(list(iter_skills()), expected)


if __name__ == "__main__":
    unittest.main()
