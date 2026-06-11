"""Unit tests for bin/gen-prerequisites.py — the prerequisites-checklist
generator (Phase 5 of the generalized-localization plan).

Covers: rendering every setup section, --check semantics (required tool
failure → exit 1; optional failure → exit 0), empty-setup hint, missing
project → exit 2, --out file writing, and that environment variable
VALUES never appear (names/purposes only).

Run with: python3 -m unittest discover -s plugins/polymath-author/tests
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import os
import pathlib
import tempfile
import unittest
from contextlib import redirect_stdout

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "plugins" / "polymath-author" / "bin" / "gen-prerequisites.py"

CONFIG = """\
schemaVersion: 1
project:
  name: refund-service
stack:
  languages:
    - lang: python
setup:
  context_sources: [README.md, AGENTS.md]
  required_tools:
    - name: python3
      version: "3.12"
      check: python3 --version
    - name: missing-optional-tool
      check: definitely-not-a-tool-xyz --version
      required: false
  environment:
    - name: API_TOKEN
      purpose: Talks to the staging API.
      required: true
  first_steps:
    - Install dependencies.
    - Run the tests once.
"""


def _import_gen():
    loader = importlib.machinery.SourceFileLoader("gen_prereqs", str(SCRIPT))
    spec = importlib.util.spec_from_loader("gen_prereqs", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class GenPrerequisitesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_gen()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / ".polymath").mkdir(parents=True)
        (self.repo / ".git").mkdir()
        (self.repo / ".polymath" / "project.yaml").write_text(CONFIG)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run(self, *argv: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = self.mod.main(list(argv))
        return code, buf.getvalue()

    def test_renders_every_section(self) -> None:
        code, out = self._run("--cwd", str(self.repo))
        self.assertEqual(code, 0)
        self.assertIn("# Prerequisites — refund-service", out)
        self.assertIn("- [ ] `README.md`", out)
        self.assertIn("python3 3.12 — verify with `python3 --version`", out)
        self.assertIn("*(optional)*", out)
        self.assertIn("`API_TOKEN` — Talks to the staging API.; required;", out)
        self.assertIn("sensitive — set locally, never commit the value", out)
        self.assertIn("1. [ ] Install dependencies.", out)
        self.assertIn("2. [ ] Run the tests once.", out)

    def test_check_mode_optional_failure_exits_zero(self) -> None:
        code, out = self._run("--cwd", str(self.repo), "--check")
        self.assertEqual(code, 0)
        self.assertIn("[x] PASS — python3 3.12", out)
        self.assertIn("[ ] FAIL — missing-optional-tool *(optional)*", out)

    def test_check_mode_required_failure_exits_one(self) -> None:
        (self.repo / ".polymath" / "project.yaml").write_text(
            CONFIG.replace("      required: false\n", "")
        )
        code, out = self._run("--cwd", str(self.repo), "--check")
        self.assertEqual(code, 1)
        self.assertIn("[ ] FAIL — missing-optional-tool", out)

    def test_out_writes_file(self) -> None:
        dest = self.repo / "docs" / "onboarding" / "prerequisites.md"
        code, _ = self._run("--cwd", str(self.repo), "--out", str(dest))
        self.assertEqual(code, 0)
        self.assertIn("# Prerequisites — refund-service", dest.read_text())

    def test_empty_setup_block_renders_hint(self) -> None:
        (self.repo / ".polymath" / "project.yaml").write_text(
            "schemaVersion: 1\nproject:\n  name: bare\n"
            "stack:\n  languages:\n    - lang: go\n"
        )
        code, out = self._run("--cwd", str(self.repo))
        self.assertEqual(code, 0)
        self.assertIn("setup block is empty", out)

    def test_no_project_exits_two(self) -> None:
        bare = pathlib.Path(self._tmp.name) / "bare"
        (bare / ".git").mkdir(parents=True)
        import contextlib
        import io as _io

        with contextlib.redirect_stderr(_io.StringIO()):
            code = self.mod.main(["--cwd", str(bare)])
        self.assertEqual(code, 2)

    def test_environment_values_never_read(self) -> None:
        os.environ["API_TOKEN"] = "super-secret-value-12345"
        try:
            code, out = self._run("--cwd", str(self.repo))
        finally:
            os.environ.pop("API_TOKEN", None)
        self.assertEqual(code, 0)
        self.assertNotIn("super-secret-value-12345", out)


if __name__ == "__main__":
    unittest.main()
