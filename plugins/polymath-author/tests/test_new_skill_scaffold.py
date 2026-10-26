"""A freshly scaffolded skill must already pass the SKILL.md shape gate
(tools/check-skill-shape.py: SKILL-2 sections, SKILL-3 mode, SKILL-4 links),
so authors start from a compliant skeleton instead of a failing one.

Run with: python3 -m unittest discover -s plugins/polymath-author/tests
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[3]
NEW_SKILL = REPO / "plugins" / "polymath-author" / "bin" / "new-skill.sh"
CHECKER = REPO / "tools" / "check-skill-shape.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_skill_shape", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class NewSkillScaffoldTest(unittest.TestCase):
    def test_scaffold_passes_shape_gate(self):
        with tempfile.TemporaryDirectory(prefix="new-skill-") as tmp:
            root = pathlib.Path(tmp)
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps({"plugins": []}))
            (root / "plugins" / "polymath-demo" / "templates").mkdir(parents=True)
            proc = subprocess.run(["bash", str(NEW_SKILL), "demo", "widget", "Draft a widget."],
                                  cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            skill_md = root / "plugins" / "polymath-demo" / "skills" / "widget" / "SKILL.md"
            errors, mode = load_checker().check(skill_md)
            self.assertEqual(errors, [])
            self.assertEqual(mode, "analytical")
            self.assertIn("`[TBD]`", skill_md.read_text())  # heredoc escaping kept the backticks


if __name__ == "__main__":
    unittest.main()
