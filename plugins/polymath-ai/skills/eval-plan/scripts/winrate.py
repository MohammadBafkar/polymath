#!/usr/bin/env python3
"""winrate — pairwise eval verdict with a Wilson score interval.

  winrate.py --wins 114 --losses 86 [--ties 23] [--confidence 0.95]

Ties are excluded from the win-rate and reported separately. The candidate
SHIPS only when the whole interval sits above 0.5; REGRESSION when it sits
below; otherwise NOT DISTINGUISHABLE from a coin flip. Also prints the
smallest win count (out of the same decisive total) that would clear 0.5.

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import math
import sys
from statistics import NormalDist


def wilson(wins: int, n: int, z: float) -> tuple[float, float]:
    p = wins / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pairwise win-rate verdict (Wilson interval).")
    ap.add_argument("--wins", type=int, required=True)
    ap.add_argument("--losses", type=int, required=True)
    ap.add_argument("--ties", type=int, default=0)
    ap.add_argument("--confidence", type=float, default=0.95)
    args = ap.parse_args(argv)
    if min(args.wins, args.losses, args.ties) < 0 or args.wins + args.losses == 0:
        print("winrate: need non-negative counts and at least one decisive comparison", file=sys.stderr)
        return 2
    if not 0.5 < args.confidence < 1:
        print("winrate: --confidence must be in (0.5, 1)", file=sys.stderr)
        return 2
    n = args.wins + args.losses
    z = NormalDist().inv_cdf(1 - (1 - args.confidence) / 2)
    lo, hi = wilson(args.wins, n, z)
    if lo > 0.5:
        verdict = "SHIP — the whole interval is above 0.5"
    elif hi < 0.5:
        verdict = "REGRESSION — the whole interval is below 0.5"
    else:
        verdict = "NOT DISTINGUISHABLE from a coin flip — collect more comparisons or don't ship"
    need = next((w for w in range(n + 1) if wilson(w, n, z)[0] > 0.5), None)
    print("\n".join([
        f"Pairwise eval: {args.wins} wins / {args.losses} losses / {args.ties} ties (ties excluded)",
        f"Win rate: {args.wins / n:.1%} of {n} decisive comparisons",
        f"{args.confidence:.0%} Wilson interval: {lo:.3f} – {hi:.3f}",
        f"Verdict: {verdict}",
        f"Wins needed to ship at n = {n}: {need if need is not None else 'not reachable'}",
    ]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
