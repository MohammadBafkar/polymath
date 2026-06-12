"""Pin tools/build-workflow-index.py (the budget owner) and
plugins/polymath-flows/hooks/scripts/project-index.py (the SessionStart
renderer) to the SAME tiering contract: constants, token arithmetic, and
tier selection must be byte-identical, or the builder's budget assertion
stops measuring what sessions actually see.

Also covers the tier-selection semantics: relevant-first deterministic
ordering, budget respected, per-entry whenToUse cap enforced by the
builder, and the renderer's end-to-end behavior in a scratch repo.

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILDER = REPO_ROOT / "tools" / "build-workflow-index.py"
RENDERER = (
    REPO_ROOT / "plugins" / "polymath-flows" / "hooks" / "scripts" / "project-index.py"
)


def _import(name: str, path: pathlib.Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class ContractPinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = _import("bwi", BUILDER)
        cls.renderer = _import("pidx", RENDERER)

    def test_constants_identical(self) -> None:
        for attr in ("INJECTION_HEADER", "INJECTION_FOOTER", "TIER_A_BUDGET", "TIER_B_POINTER"):
            self.assertEqual(
                getattr(self.builder, attr), getattr(self.renderer, attr),
                f"{attr} drifted between builder and renderer",
            )

    def test_token_arithmetic_identical(self) -> None:
        for n in range(0, 64):
            text = "x" * n
            self.assertEqual(
                self.builder.estimate_tokens(text), self.renderer.estimate_tokens(text)
            )

    def test_tier_selection_identical_on_real_index(self) -> None:
        mini = json.loads(
            (REPO_ROOT / "plugins" / "polymath-flows" / "data" / "workflow-index.min.json").read_text()
        )
        for relevant in (set(), {mini[-1]["n"]}, {r["n"] for r in mini}):
            b_a, b_b = self.builder.select_tier_a(mini, relevant)
            r_a, r_b = self.renderer.select_tier_a(mini, relevant)
            self.assertEqual(b_a, r_a)
            self.assertEqual(b_b, r_b)


class TierSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _import("bwi2", BUILDER)

    def _records(self, n: int) -> list[dict]:
        return [{"n": f"wf{i:02d}", "w": "x" * 60} for i in range(n)]

    def test_relevant_records_come_first(self) -> None:
        records = self._records(20)
        tier_a, _ = self.mod.select_tier_a(records, relevant={"wf19", "wf18"})
        self.assertEqual([r["n"] for r in tier_a[:2]], ["wf18", "wf19"])

    def test_budget_respected_and_split_deterministic(self) -> None:
        records = self._records(40)  # 40 × ~19 tokens ≫ budget
        tier_a, tier_b = self.mod.select_tier_a(records, relevant=set())
        rendered = self.mod.render_injection(records)
        self.assertLessEqual(self.mod.estimate_tokens(rendered), self.mod.TIER_A_BUDGET)
        self.assertEqual(len(tier_a) + len(tier_b), 40)
        self.assertGreater(len(tier_b), 0)
        # Determinism: same inputs, same split.
        again_a, _ = self.mod.select_tier_a(records, relevant=set())
        self.assertEqual(tier_a, again_a)

    def test_everything_fits_means_no_pointer(self) -> None:
        records = self._records(3)
        rendered = self.mod.render_injection(records)
        self.assertNotIn("…plus", rendered)

    def test_when_to_use_cap_is_enforced_by_builder(self) -> None:
        self.assertLessEqual(
            max(len(r["w"]) for r in json.loads(
                (REPO_ROOT / "plugins" / "polymath-flows" / "data" / "workflow-index.min.json").read_text()
            )),
            self.mod.WHEN_TO_USE_MAX_CHARS,
        )


class RendererEndToEndTests(unittest.TestCase):
    def _run(self, scratch: pathlib.Path, detect: list[dict] | None) -> tuple[str, dict]:
        mini = [
            {"n": "alpha", "w": "Alpha things."},
            {"n": "beta", "w": "Beta things."},
            {"n": "gamma", "w": "Gamma things."},
        ]
        full = [{**r, "t": []} for r in mini]
        (scratch / "min.json").write_text(json.dumps(mini))
        (scratch / "full.json").write_text(json.dumps(full))
        argv = [sys.executable, str(RENDERER), str(scratch / "min.json"),
                str(scratch / "full.json"), str(scratch / "pdata")]
        if detect is not None:
            (scratch / "detect.json").write_text(json.dumps(detect))
            argv.append(str(scratch / "detect.json"))
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=15, cwd=scratch,
        )
        fragment = {}
        frag_path = scratch / "pdata" / "polymath-flows" / "workflow-index.project.json"
        if frag_path.exists():
            fragment = json.loads(frag_path.read_text())
        return proc.stdout, fragment

    def test_relevant_workflow_listed_first_and_tiering_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scratch = pathlib.Path(tmp)
            (scratch / ".git").mkdir()
            (scratch / "Dockerfile").write_text("FROM scratch\n")
            out, fragment = self._run(
                scratch,
                detect=[{"n": "gamma", "paths": ["Dockerfile"]}],
            )
            lines = [l for l in out.splitlines() if l.startswith("  - ")]
            self.assertTrue(lines and lines[0].startswith("  - gamma:"), out)
            tiering = fragment.get("tiering") or {}
            self.assertEqual(tiering.get("relevant"), ["gamma"])
            self.assertEqual(tiering.get("overflow_relevant"), [])
            self.assertIn("alpha", tiering.get("tier_a") or [])

    def test_no_detect_index_is_alphabetical_and_fail_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scratch = pathlib.Path(tmp)
            (scratch / ".git").mkdir()
            out, _ = self._run(scratch, detect=None)
            lines = [l for l in out.splitlines() if l.startswith("  - ")]
            self.assertEqual([l.split(":")[0] for l in lines],
                             ["  - alpha", "  - beta", "  - gamma"])


if __name__ == "__main__":
    unittest.main()
