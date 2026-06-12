"""Unit tests for tools/lib/textsim.py.

Pins jaccard() to the (verified-equivalent) set-level arithmetic of
check-command-overlap.py and lint-descriptions.py, including the empty-set
cases where the two originals took different code paths to the same 0.0.

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.lib.textsim import jaccard  # noqa: E402


class JaccardTests(unittest.TestCase):
    def test_identical_sets(self) -> None:
        self.assertEqual(jaccard({"a", "b"}, {"a", "b"}), 1.0)

    def test_disjoint_sets(self) -> None:
        self.assertEqual(jaccard({"a"}, {"b"}), 0.0)

    def test_partial_overlap(self) -> None:
        self.assertEqual(jaccard({"a", "b", "c"}, {"b", "c", "d"}), 0.5)

    def test_empty_either_side_is_zero(self) -> None:
        # check-command-overlap's early return; lint-descriptions' zero
        # numerator — both originals yield 0.0 here.
        self.assertEqual(jaccard(set(), {"a"}), 0.0)
        self.assertEqual(jaccard({"a"}, set()), 0.0)
        self.assertEqual(jaccard(set(), set()), 0.0)

    def test_equivalence_with_lint_descriptions_formula(self) -> None:
        """len(a & b) / max(1, len(a | b)) — must agree on every case."""
        cases = [
            (set(), set()),
            (set(), {"a"}),
            ({"a"}, {"a"}),
            ({"a", "b", "c"}, {"b", "c", "d"}),
            ({"x"}, {"y", "z"}),
        ]
        for a, b in cases:
            self.assertEqual(jaccard(a, b), len(a & b) / max(1, len(a | b)), msg=f"{a} vs {b}")

    def test_accepts_any_iterable(self) -> None:
        self.assertEqual(jaccard(["a", "b", "b"], ("b", "a")), 1.0)


if __name__ == "__main__":
    unittest.main()
