"""Unit tests for hooks/scripts/project-index.py — the SessionStart renderer
that injects the catalog workflow index plus the machine-local project/user
fragment.

Pinned behavior:
  - byte-identical catalog rendering when no project/user workflows exist
    (zero-config repos keep today's exact injection)
  - project tier indexed, catalog shadowing annotated
  - user tier indexed and shadowed by the project tier on name collision
  - trigger-collision DROP (vs catalog and vs earlier tiers), recorded in
    dropped_triggers — never an error
  - fragment file written under <data_root>/polymath-flows/
  - fail-open: malformed YAML and missing whenToUse are skipped
  - the no-PyYAML metadata extraction fallback

Run with: python3 -m unittest discover -s plugins/polymath-flows/tests
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import pathlib
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT / "plugins" / "polymath-flows" / "hooks" / "scripts" / "project-index.py"
)
DATA_DIR = REPO_ROOT / "plugins" / "polymath-flows" / "data"


def _import_script():
    loader = importlib.machinery.SourceFileLoader("project_index", str(SCRIPT))
    spec = importlib.util.spec_from_loader("project_index", loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WORKFLOW_TMPL = (
    "schemaVersion: 0.1\n"
    "name: {name}\n"
    "version: 0.1.0\n"
    "whenToUse: {when}\n"
    "{triggers}"
    "steps:\n"
    "  - id: only\n"
    "    invoke: a:b\n"
    "    prompt: Do.\n"
)


class ProjectIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _import_script()
        self._tmp = tempfile.TemporaryDirectory()
        self.work = pathlib.Path(self._tmp.name)
        self._prev_cwd = pathlib.Path.cwd()
        os.chdir(self.work)
        self._prev_cfg = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.work / ".cfg")
        # The ~/.claude user fallback is also indexed; pin HOME so a real
        # machine's user workflows can't leak into these tests.
        self._prev_home = os.environ.get("HOME")
        os.environ["HOME"] = str(self.work / ".home")
        self.data_root = self.work / ".pdata"
        self.min_index = DATA_DIR / "workflow-index.min.json"
        self.full_index = DATA_DIR / "workflow-index.json"

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        if self._prev_cfg is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self._prev_cfg
        if self._prev_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self._prev_home
        self._tmp.cleanup()

    def _run(self) -> str:
        from contextlib import redirect_stdout
        from io import StringIO

        buf = StringIO()
        with redirect_stdout(buf):
            rc = self.mod.main(
                ["project-index.py", str(self.min_index), str(self.full_index), str(self.data_root)]
            )
        self.assertEqual(rc, 0)
        return buf.getvalue()

    def _write_project_workflow(self, name: str, when: str, triggers: list[str] | None = None) -> None:
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        tblock = ""
        if triggers:
            tblock = "triggers:\n" + "".join(f'  - "{t}"\n' for t in triggers)
        (wf_dir / f"{name}.yaml").write_text(
            WORKFLOW_TMPL.format(name=name, when=when, triggers=tblock)
        )

    def _write_user_workflow(self, name: str, when: str, triggers: list[str] | None = None) -> None:
        wf_dir = self.work / ".cfg" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        tblock = ""
        if triggers:
            tblock = "triggers:\n" + "".join(f'  - "{t}"\n' for t in triggers)
        (wf_dir / f"{name}.yaml").write_text(
            WORKFLOW_TMPL.format(name=name, when=when, triggers=tblock)
        )

    def _fragment(self) -> dict:
        return json.loads(
            (self.data_root / "polymath-flows" / "workflow-index.project.json").read_text()
        )

    def test_no_project_workflows_is_byte_identical_to_catalog(self) -> None:
        out = self._run()
        records = json.loads(self.min_index.read_text())
        expected_lines = [self.mod.INJECTION_HEADER]
        expected_lines += [f"  - {r['n']}: {r['w']}" for r in records]
        expected_lines.append(self.mod.INJECTION_FOOTER)
        self.assertEqual(out, "\n".join(expected_lines) + "\n")
        self.assertEqual(self._fragment()["entries"], [])

    def test_project_workflow_indexed_and_injected(self) -> None:
        self._write_project_workflow(
            "deployAcme", "Deploy the Acme stack to staging.", ["deploy acme to staging"]
        )
        out = self._run()
        self.assertIn("  - deployAcme: Deploy the Acme stack to staging.", out)
        frag = self._fragment()
        self.assertEqual(frag["entries"][0]["n"], "deployAcme")
        self.assertEqual(frag["entries"][0]["tier"], "project")
        self.assertEqual(frag["entries"][0]["t"], ["deploy acme to staging"])
        self.assertNotIn("shadows", frag["entries"][0])

    def test_catalog_shadow_annotated(self) -> None:
        self._write_project_workflow("shipFeature", "Acme-localized shipFeature.")
        out = self._run()
        self.assertIn(
            "  - shipFeature: Acme-localized shipFeature. "
            "[overrides the catalog workflow of this name]",
            out,
        )
        self.assertTrue(self._fragment()["entries"][0]["shadows"])

    def test_catalog_trigger_collision_dropped(self) -> None:
        full = json.loads(self.full_index.read_text())
        catalog_trigger = full[0]["t"][0]
        owner = full[0]["n"]
        self._write_project_workflow(
            "deployAcme", "Deploy.", [catalog_trigger, "deploy acme now"]
        )
        self._run()
        frag = self._fragment()
        self.assertEqual(frag["entries"][0]["t"], ["deploy acme now"])
        self.assertEqual(
            frag["dropped_triggers"],
            [{"n": "deployAcme", "trigger": catalog_trigger, "collides_with": owner}],
        )

    def test_project_tier_shadows_user_tier(self) -> None:
        self._write_project_workflow("deployAcme", "Project variant.")
        self._write_user_workflow("deployAcme", "User variant.")
        self._write_user_workflow("myUserFlow", "Personal arc.", ["my weekly arc"])
        out = self._run()
        self.assertIn("  - deployAcme: Project variant.", out)
        self.assertNotIn("User variant.", out)
        self.assertIn("  - myUserFlow: Personal arc. [user layer]", out)
        tiers = {e["n"]: e["tier"] for e in self._fragment()["entries"]}
        self.assertEqual(tiers, {"deployAcme": "project", "myUserFlow": "user"})

    def test_cross_tier_trigger_collision_dropped(self) -> None:
        self._write_project_workflow("deployAcme", "Project.", ["deploy acme to staging"])
        self._write_user_workflow("myUserFlow", "Personal.", ["deploy acme to staging"])
        self._run()
        frag = self._fragment()
        by_name = {e["n"]: e for e in frag["entries"]}
        self.assertEqual(by_name["deployAcme"]["t"], ["deploy acme to staging"])
        self.assertEqual(by_name["myUserFlow"]["t"], [])
        self.assertEqual(
            frag["dropped_triggers"],
            [
                {
                    "n": "myUserFlow",
                    "trigger": "deploy acme to staging",
                    "collides_with": "deployAcme",
                }
            ],
        )

    def test_stem_wins_over_declared_name(self) -> None:
        """`start` resolves by FILE STEM, so the index must advertise the
        stem — a file local-ship.yaml declaring `name: shipFeature` must
        not claim to override the catalog shipFeature."""
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        (wf_dir / "local-ship.yaml").write_text(
            WORKFLOW_TMPL.format(
                name="shipFeature", when="Acme-localized shipFeature.", triggers=""
            )
        )
        out = self._run()
        self.assertIn("  - local-ship: Acme-localized shipFeature.", out)
        self.assertNotIn("overrides the catalog workflow", out)
        entry = self._fragment()["entries"][0]
        self.assertEqual(entry["n"], "local-ship")
        self.assertEqual(entry["declaredName"], "shipFeature")
        self.assertNotIn("shadows", entry)

    def test_multiline_whentouse_skipped_oneline_block_scalar_indexed(self) -> None:
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        (wf_dir / "multiline.yaml").write_text(
            "schemaVersion: 0.1\nname: multiline\nversion: 0.1.0\n"
            "whenToUse: |\n  Deploy the stack\n  with two lines.\n"
            "steps:\n  - id: a\n    invoke: a:b\n    prompt: x\n"
        )
        (wf_dir / "oneliner.yaml").write_text(
            "schemaVersion: 0.1\nname: oneliner\nversion: 0.1.0\n"
            "whenToUse: |\n  Deploy the stack.\n"
            "steps:\n  - id: a\n    invoke: a:b\n    prompt: x\n"
        )
        out = self._run()
        self.assertNotIn("multiline", out)
        self.assertIn("  - oneliner: Deploy the stack.\n", out + "\n")
        names = [e["n"] for e in self._fragment()["entries"]]
        self.assertEqual(names, ["oneliner"])

    def test_malformed_and_unindexable_yaml_skipped(self) -> None:
        wf_dir = self.work / ".claude" / "polymath" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        (wf_dir / "broken.yaml").write_text(": : not yaml [\n  - {")
        (wf_dir / "noWhen.yaml").write_text(
            "schemaVersion: 0.1\nname: noWhen\nversion: 0.1.0\n"
            "steps:\n  - id: a\n    invoke: a:b\n    prompt: x\n"
        )
        out = self._run()
        self.assertNotIn("noWhen", out)
        self.assertEqual(self._fragment()["entries"], [])

    def _extract_meta_no_pyyaml(self, text: str) -> dict:
        # Force the regex fallback by shadowing the yaml import.
        import builtins

        real_import = builtins.__import__

        def no_yaml(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("forced for test")
            return real_import(name, *args, **kwargs)

        builtins.__import__ = no_yaml
        try:
            return self.mod._extract_meta(text)
        finally:
            builtins.__import__ = real_import

    def test_extract_meta_fallback_without_pyyaml(self) -> None:
        text = (
            "schemaVersion: 0.1\n"
            "name: deployAcme\n"
            'whenToUse: "Deploy the Acme stack."\n'
            "triggers:\n"
            '  - "deploy acme to staging"\n'
            "  - 'ship the acme way'\n"
            "steps:\n"
            "  - id: a\n"
        )
        meta = self._extract_meta_no_pyyaml(text)
        self.assertEqual(meta["name"], "deployAcme")
        self.assertEqual(meta["whenToUse"], "Deploy the Acme stack.")
        self.assertEqual(
            meta["triggers"], ["deploy acme to staging", "ship the acme way"]
        )

    def test_extract_meta_fallback_reads_flatten_output(self) -> None:
        """The canonical producer of project workflows is `polymath-flow
        flatten` (yaml.safe_dump: column-0 sequence items, one-line plain
        scalars). The no-PyYAML fallback must read its output."""
        import yaml

        text = yaml.safe_dump(
            {
                "schemaVersion": 0.1,
                "name": "shipFeature",
                "version": "0.1.0",
                "whenToUse": (
                    "Take a described feature from requirements through "
                    "implementation, tests, and review to a draft PR — the "
                    "default arc for shipping a small feature."
                ),
                "triggers": ["ship this feature", "build this feature for me"],
                "steps": [{"id": "a", "invoke": "a:b", "prompt": "x"}],
            },
            sort_keys=False,
            width=4096,
        )
        meta = self._extract_meta_no_pyyaml(text)
        self.assertEqual(meta["name"], "shipFeature")
        self.assertTrue(str(meta["whenToUse"]).endswith("small feature."))
        self.assertEqual(
            meta["triggers"], ["ship this feature", "build this feature for me"]
        )

    def test_extract_meta_fallback_null_and_block_whentouse(self) -> None:
        """A null `whenToUse:` must not capture the next line, and a
        block-scalar indicator must normalize to not-indexed."""
        null_when = "name: x\nwhenToUse:\ntriggers:\n  - 'a phrase here'\n"
        meta = self._extract_meta_no_pyyaml(null_when)
        self.assertIsNone(self.mod._normalize_when(meta["whenToUse"]))
        block_when = "name: x\nwhenToUse: |\n  Multi\n  line.\n"
        meta = self._extract_meta_no_pyyaml(block_when)
        self.assertIsNone(self.mod._normalize_when(meta["whenToUse"]))


if __name__ == "__main__":
    unittest.main()
