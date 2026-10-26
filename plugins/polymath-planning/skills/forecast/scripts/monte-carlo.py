#!/usr/bin/env python3
"""monte-carlo — throughput Monte Carlo delivery forecast, seeded and repeatable.

Resamples historical per-period throughput (items finished per week, or per
sprint) with replacement. Same inputs + same seed = byte-identical output.

  When will N items be done?
    monte-carlo.py --throughput 3,5,2,4,6,0,4,5 --items 40
  How many items fit in W periods?
    monte-carlo.py --throughput 3,5,2,4,6,0,4,5 --periods 10

Percentiles use the nearest-rank method. For "when", the P85 line reads "85% of
simulations finished within this many periods"; for "how many", it reads "85%
of simulations finished at least this many items" (the 15th percentile of the
distribution — the conservative end).

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import math
import random
import sys

LEVELS = (50, 70, 85, 95)
MIN_SAMPLES = 6
MAX_PERIODS = 1000


class InputError(Exception):
    pass


def parse_throughput(text: str) -> list[int]:
    try:
        vals = [int(x) for x in text.replace(" ", "").split(",") if x != ""]
    except ValueError:
        raise InputError("--throughput must be comma-separated whole numbers (items per period)")
    if not vals:
        raise InputError("--throughput is empty")
    if any(v < 0 for v in vals):
        raise InputError("--throughput values must be >= 0")
    if sum(vals) == 0:
        raise InputError("--throughput is all zeros: no delivery history to sample")
    return vals


def nearest_rank(sorted_vals: list[int], pct: float) -> int:
    k = max(1, math.ceil(pct / 100 * len(sorted_vals)))
    return sorted_vals[k - 1]


def simulate_when(hist: list[int], items: int, trials: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    out = []
    for _ in range(trials):
        done = periods = 0
        while done < items:
            done += rng.choice(hist)
            periods += 1
            if periods > MAX_PERIODS:
                raise InputError(f"a simulation exceeded {MAX_PERIODS} periods — history is too sparse for {items} items")
        out.append(periods)
    return sorted(out)


def simulate_how_many(hist: list[int], periods: int, trials: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return sorted(sum(rng.choice(hist) for _ in range(periods)) for _ in range(trials))


def render(args, hist: list[int], dist: list[int]) -> str:
    unit = args.unit
    n = len(hist)
    head = [
        "Forecast (throughput Monte Carlo)",
        f"History:  {n} {unit}s, items/{unit} = {','.join(map(str, hist))}"
        f"  (median {sorted(hist)[(n - 1) // 2]}, mean {sum(hist) / n:.1f})",
        f"Trials:   {args.trials}  seed {args.seed}",
    ]
    if args.items is not None:
        head.append(f"Question: when are {args.items} items done?")
        body = [f"  P{lv:<3} done within {nearest_rank(dist, lv)} {unit}s" for lv in LEVELS]
    else:
        head.append(f"Question: how many items in {args.periods} {unit}s?")
        body = [f"  P{lv:<3} at least {nearest_rank(dist, 100 - lv)} items" for lv in LEVELS]
    warn = []
    if n < MIN_SAMPLES:
        warn.append(f"WARNING: only {n} {unit}s of history — under {MIN_SAMPLES}, treat the range as a cone of uncertainty.")
    if hist.count(0) * 2 > n:
        warn.append(f"WARNING: most {unit}s delivered 0 items — check the history is per-{unit} throughput, not a typo.")
    return "\n".join(head + ["", "Result:"] + body + ([""] + warn if warn else []))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Seeded throughput Monte Carlo forecast.")
    ap.add_argument("--throughput", required=True, help="items finished per period, oldest first: 3,5,2,4")
    q = ap.add_mutually_exclusive_group(required=True)
    q.add_argument("--items", type=int, help="remaining scope in items → periods to finish")
    q.add_argument("--periods", type=int, help="horizon in periods → items that fit")
    ap.add_argument("--trials", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--unit", default="week", help="period name for the output (week, sprint)")
    args = ap.parse_args(argv)
    try:
        hist = parse_throughput(args.throughput)
        if args.trials < 1000:
            raise InputError("--trials must be >= 1000")
        if args.items is not None:
            if args.items < 1:
                raise InputError("--items must be >= 1")
            dist = simulate_when(hist, args.items, args.trials, args.seed)
        else:
            if args.periods < 1:
                raise InputError("--periods must be >= 1")
            dist = simulate_how_many(hist, args.periods, args.trials, args.seed)
        print(render(args, hist, dist))
    except InputError as e:
        print(f"monte-carlo: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
