"""estimate_tokens(): the ONE canonical chars-to-tokens heuristic.

``tokens = (chars + 3) // 4`` — ceil(chars/4). This is the arithmetic the
always-on budget gate (``tools/token-report.py budget``) runs on. The one
remaining divergent estimator is tools/build-workflow-index.py's
``_count_tokens`` (tiktoken when importable, else ``len(text) // 4 + 1``):
its fallback disagrees with this function exactly when ``chars % 4 == 0``
(e.g. polymath-release: chars=1572 -> 393 vs 394), and its tiktoken branch
is environment-dependent (tiktoken is installed neither locally nor in CI),
which a deterministic budget gate cannot tolerate — so it was NOT adopted
as canonical. tests/tools/test_tokens.py pins both the arithmetic and the
divergence point.
"""
from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Estimate the token cost of `text` as ceil(len/4); 0 for empty."""
    return (len(text) + 3) // 4
