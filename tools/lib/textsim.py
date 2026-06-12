"""Description-similarity helpers shared by the linters.

jaccard() consolidates the two implementations in check-command-overlap.py
(``_jaccard`` over pre-tokenized sets, early-returning 0.0 when either side
is empty) and lint-descriptions.py (``_jaccard`` over strings, computing
``len(ta & tb) / max(1, len(ta | tb))`` after its own tokenizer). The
set-level arithmetic of the two is equivalent in every case:

  - either side empty: the intersection is empty, so both return 0.0
    (check-command-overlap via the early return; lint-descriptions via a
    zero numerator — its ``max(1, ...)`` only guards the both-empty
    division)
  - both non-empty: the identical formula ``|a & b| / |a | b|``

so ONE canonical function suffices. What the two tools do NOT share is
tokenization (stoplists, stemming, name-token dropping differ); that stays
tool-local and out of scope here — jaccard() takes already-tokenized sets.
"""
from __future__ import annotations

from collections.abc import Hashable, Iterable


def jaccard(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """Jaccard similarity of two token collections; 0.0 if either is empty."""
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
