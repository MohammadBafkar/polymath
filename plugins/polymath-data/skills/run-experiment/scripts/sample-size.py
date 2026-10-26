#!/usr/bin/env python3
"""sample-size — A/B(/n) experiment sizing, duration, and SRM check.

Sizing (per variant, two-sided test, normal approximation):
  mean:        n = 2 (z_a + z_b)^2 σ^2 / δ^2
  proportion:  n = (z_a √(2 p̄(1−p̄)) + z_b √(p1(1−p1) + p2(1−p2)))^2 / δ^2
               p1 = baseline, p2 = baseline + δ, p̄ = (p1 + p2) / 2
  With k > 2 variants, each treatment is compared to control at α / (k − 1)
  (Bonferroni).

  sample-size.py --metric mean --sigma 2000 --mde 100 --daily-eligible 80000
  sample-size.py --metric proportion --baseline 0.12 --mde 0.01 --daily-eligible 30000 --allocation 0.5

Duration = variants × n ÷ (daily eligible × allocation), then rounded UP to
whole weeks with a 7-day floor (weekday/weekend cycles). Over the 28-day cap the
verdict is UNDERPOWERED and the MDE detectable in 28 days is printed.

Sample-ratio mismatch (run before reading any metric):
  sample-size.py --srm 50421,49579 [--split 50,50]
  chi-square goodness of fit, df = k − 1; p < 0.001 = SRM, results are void.

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import math
import sys
from statistics import NormalDist

CAP_DAYS = 28
SRM_P = 0.001


class InputError(Exception):
    pass


def z_values(alpha: float, power: float, variants: int) -> tuple[float, float, float]:
    a = alpha / (variants - 1)
    nd = NormalDist()
    return a, nd.inv_cdf(1 - a / 2), nd.inv_cdf(power)


def n_mean(sigma: float, mde: float, za: float, zb: float) -> float:
    return 2 * (za + zb) ** 2 * sigma ** 2 / mde ** 2


def n_prop(p1: float, mde: float, za: float, zb: float) -> float:
    p2 = p1 + mde
    if not 0 < p2 < 1:
        raise InputError(f"baseline + MDE = {p2:g} is outside (0, 1)")
    pbar = (p1 + p2) / 2
    num = za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return num ** 2 / mde ** 2


def mde_at(n: int, args, za: float, zb: float) -> float:
    """Smallest absolute MDE detectable with n per variant."""
    if args.metric == "mean":
        return math.sqrt(2 * (za + zb) ** 2 * args.sigma ** 2 / n)
    lo, hi = 1e-9, (1 - args.baseline) - 1e-9
    if n_prop(args.baseline, hi, za, zb) > n:
        return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        if n_prop(args.baseline, mid, za, zb) > n:
            lo = mid
        else:
            hi = mid
    return hi


def chi2_sf(x: float, df: int) -> float:
    """Upper tail of the chi-square distribution: Q(df/2, x/2)."""
    a, xx = df / 2, x / 2
    if xx <= 0:
        return 1.0
    gln = math.lgamma(a)
    if xx < a + 1:  # series for P, return 1 − P
        ap, s, d = a, 1 / a, 1 / a
        for _ in range(1000):
            ap += 1
            d *= xx / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return max(0.0, 1 - s * math.exp(-xx + a * math.log(xx) - gln))
    b = xx + 1 - a  # continued fraction for Q (Lentz)
    c, d = 1 / 1e-300, 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return math.exp(-xx + a * math.log(xx) - gln) * h


def srm(args) -> str:
    try:
        counts = [int(x) for x in args.srm.split(",")]
        split = [float(x) for x in args.split.split(",")] if args.split else [1.0] * len(counts)
    except ValueError:
        raise InputError("--srm and --split take comma-separated numbers")
    if len(counts) < 2 or len(split) != len(counts) or min(counts) < 0 or min(split) <= 0:
        raise InputError("--srm needs ≥ 2 non-negative counts and --split one positive share per count")
    total = sum(counts)
    if total == 0:
        raise InputError("--srm counts are all zero")
    expected = [total * s / sum(split) for s in split]
    stat = sum((o - e) ** 2 / e for o, e in zip(counts, expected))
    p = chi2_sf(stat, len(counts) - 1)
    verdict = "SRM DETECTED — assignment is broken; do not read any metric" if p < SRM_P else "no SRM — assignment matches the planned split"
    return "\n".join([
        "Sample-ratio mismatch check",
        f"Observed: {', '.join(f'{c:,}' for c in counts)}  (total {total:,})",
        f"Expected: {', '.join(f'{e:,.1f}' for e in expected)}  (split {args.split or 'equal'})",
        f"Chi-square = {stat:.3f}, df = {len(counts) - 1}, p = {p:.4g}  (threshold p < {SRM_P})",
        f"Verdict:  {verdict}",
    ])


def sizing(args) -> str:
    if not 0 < args.alpha < 1 or not 0 < args.power < 1:
        raise InputError("--alpha and --power must be in (0, 1)")
    if args.variants < 2:
        raise InputError("--variants must be >= 2")
    if args.mde is None and args.mde_relative is None:
        raise InputError("give --mde (absolute) or --mde-relative (percent of baseline)")
    a, za, zb = z_values(args.alpha, args.power, args.variants)
    if args.metric == "mean":
        if args.sigma is None or args.sigma <= 0:
            raise InputError("--metric mean needs --sigma > 0 (per-unit standard deviation)")
        if args.mde_relative is not None:
            if args.baseline is None:
                raise InputError("--mde-relative needs --baseline")
            args.mde = abs(args.baseline) * args.mde_relative / 100
        if args.mde <= 0:
            raise InputError("MDE must be > 0")
        n = n_mean(args.sigma, args.mde, za, zb)
        desc = f"mean, σ = {args.sigma:,g}, MDE = {args.mde:,g} (absolute)"
    else:
        if args.baseline is None or not 0 < args.baseline < 1:
            raise InputError("--metric proportion needs --baseline in (0, 1)")
        if args.mde_relative is not None:
            args.mde = args.baseline * args.mde_relative / 100
        if args.mde <= 0:
            raise InputError("MDE must be > 0")
        n = n_prop(args.baseline, args.mde, za, zb)
        desc = f"proportion, baseline = {args.baseline:g}, MDE = {args.mde:g} absolute ({args.mde / args.baseline:.1%} relative)"
    n = math.ceil(n)
    out = [
        f"Experiment sizing (two-sided, α = {args.alpha:g}, power = {args.power:g}, {args.variants} variants)",
        f"Metric:   {desc}",
    ]
    if args.variants > 2:
        out.append(f"Bonferroni: {args.variants - 1} comparisons vs control → α per comparison = {a:.4g}")
    out += [
        f"z:        z(1−α/2) = {za:.3f}, z(power) = {zb:.3f}",
        f"n per variant: {n:,}   (total {n * args.variants:,})",
    ]
    if args.daily_eligible is None:
        out.append("Duration: [TBD: daily eligible units — pass --daily-eligible]")
        return "\n".join(out)
    if args.daily_eligible <= 0 or not 0 < args.allocation <= 1:
        raise InputError("--daily-eligible must be > 0 and --allocation in (0, 1]")
    per_day = args.daily_eligible * args.allocation
    raw = args.variants * n / per_day
    run = max(7, 7 * math.ceil(raw / 7))
    out += [
        f"Traffic:  {args.daily_eligible:,g} eligible/day × {args.allocation:.0%} in experiment",
        f"Duration: {raw:,.2f} days of traffic → run {run} days (whole weeks, 7-day floor)",
    ]
    if run <= CAP_DAYS:
        out.append(f"Verdict:  OK — within the {CAP_DAYS}-day cap")
    else:
        n28 = math.floor(CAP_DAYS * per_day / args.variants)
        m = mde_at(n28, args, za, zb)
        reach = "no MDE is detectable" if math.isnan(m) else f"the detectable MDE is {m:,.4g} (absolute)"
        out.append(
            f"Verdict:  UNDERPOWERED — needs {run} days > {CAP_DAYS}-day cap. In {CAP_DAYS} days "
            f"(n = {n28:,}/variant) {reach}; raise the MDE or the allocation, or accept a longer run explicitly."
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="A/B(/n) sizing, duration, SRM check.")
    ap.add_argument("--metric", choices=["mean", "proportion"])
    ap.add_argument("--sigma", type=float, help="per-unit standard deviation (mean metrics)")
    ap.add_argument("--baseline", type=float, help="baseline rate (proportion) or mean")
    ap.add_argument("--mde", type=float, help="minimum detectable effect, absolute")
    ap.add_argument("--mde-relative", type=float, help="minimum detectable effect, percent of baseline")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.8)
    ap.add_argument("--variants", type=int, default=2)
    ap.add_argument("--daily-eligible", type=float, help="eligible randomization units per day")
    ap.add_argument("--allocation", type=float, default=1.0, help="fraction of eligible traffic in the experiment")
    ap.add_argument("--srm", help="observed assignment counts, e.g. 50421,49579")
    ap.add_argument("--split", help="planned split, e.g. 50,50 (default equal)")
    args = ap.parse_args(argv)
    try:
        if args.srm:
            print(srm(args))
        elif args.metric:
            print(sizing(args))
        else:
            raise InputError("give --metric (sizing) or --srm (sample-ratio check)")
    except InputError as e:
        print(f"sample-size: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
