"""Unit tests for tools/lib/tokens.py.

Pins estimate_tokens to token-report.py budget's arithmetic — (chars + 3) / 4 —
and pins the documented divergence from build-workflow-index.py's fallback
(chars // 4 + 1) at chars % 4 == 0, which is why that heuristic was NOT
adopted as canonical.

Run with: python3 -m unittest discover -s tests/tools
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.lib.tokens import estimate_tokens  # noqa: E402


class EstimateTokensTests(unittest.TestCase):
    def test_empty_is_zero(self) -> None:
        self.assertEqual(estimate_tokens(""), 0)

    def test_ceiling_behavior(self) -> None:
        self.assertEqual(estimate_tokens("x"), 1)
        self.assertEqual(estimate_tokens("xxxx"), 1)
        self.assertEqual(estimate_tokens("xxxxx"), 2)

    def test_matches_token_budget_sh_arithmetic_exhaustively(self) -> None:
        """(chars + 3) / 4 in bash integer arithmetic, for every length 0..200."""
        for n in range(201):
            self.assertEqual(estimate_tokens("x" * n), (n + 3) // 4, msg=f"chars={n}")

    def test_diverges_from_build_workflow_index_fallback_on_multiples_of_4(self) -> None:
        """The decision pin: build-workflow-index's `len // 4 + 1` over-counts
        by one whenever chars % 4 == 0 (14 of 37 plugins on the budget inputs
        measured for the consolidation), so it was not adopted."""
        for n in (4, 8, 1572):  # 1572 = polymath-release's measured char count
            text = "x" * n
            self.assertEqual(estimate_tokens(text), n // 4)
            self.assertNotEqual(estimate_tokens(text), n // 4 + 1)
        for n in (1, 2, 3, 5, 1571):  # non-multiples: the two heuristics agree
            text = "x" * n
            self.assertEqual(estimate_tokens(text), n // 4 + 1)


if __name__ == "__main__":
    unittest.main()
