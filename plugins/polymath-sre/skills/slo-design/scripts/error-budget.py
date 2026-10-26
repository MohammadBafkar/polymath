#!/usr/bin/env python3
"""error-budget — SLO error-budget arithmetic, burn-rate alerts, and budget state.

  error-budget.py --slo 99.5 --window-days 28
      budget in minutes and h/m/s, plus the multi-window multi-burn-rate alert
      table (Google SRE workbook shape) computed for this window.

  error-budget.py --slo 99.5 --window-days 28 --consumed-minutes 140
  error-budget.py --slo 99.5 --window-days 28 --requests 2000000 --failed 7300
      adds the budget STATE for an error-budget policy:
      HEALTHY < 50% consumed, ERODING 50–100%, EXHAUSTED > 100%.

budget = (1 − SLO) × window. burn rate = budget fraction × window hours ÷ long
window hours. Seconds round half-up; burn rates print to 2 decimals.

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import sys
from decimal import ROUND_HALF_UP, Decimal

# (long window h, short window, budget fraction consumed, severity) — SRE workbook.
ALERTS = [
    (1, "5m", Decimal("0.02"), "page"),
    (6, "30m", Decimal("0.05"), "page"),
    (72, "6h", Decimal("0.10"), "ticket"),
]
LONG_LABEL = {1: "1h", 6: "6h", 72: "3d"}


class InputError(Exception):
    pass


def hms(minutes: Decimal) -> str:
    total = int((minutes * 60).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if h or m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def q2(x: Decimal) -> str:
    return str(x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def compute(slo: Decimal, days: int) -> dict:
    window_min = Decimal(days) * 24 * 60
    frac = (Decimal(100) - slo) / 100
    budget = frac * window_min
    window_h = Decimal(days) * 24
    alerts = [
        (LONG_LABEL[lw], sw, f"{int(pct * 100)}%", q2(pct * window_h / lw), sev)
        for lw, sw, pct, sev in ALERTS
    ]
    return {"window_min": window_min, "frac": frac, "budget": budget, "alerts": alerts}


def state(pct_consumed: Decimal) -> str:
    if pct_consumed > 100:
        return "EXHAUSTED"
    if pct_consumed >= 50:
        return "ERODING"
    return "HEALTHY"


def render(args, slo: Decimal, r: dict) -> str:
    d = args.window_days
    budget = r["budget"]
    out = [
        f"SLO {slo}% over a {d}-day rolling window",
        f"Window:  {r['window_min']:,} min",
        f"Budget:  {q2(r['frac'] * 100)}% × {r['window_min']:,} min = "
        f"{budget.normalize():,f} min = {hms(budget)} per {d}d",
        "",
        "Burn-rate alerts (fire only when BOTH windows exceed the rate):",
        "  Long  Short  Budget  Burn rate  Severity",
    ]
    for lw, sw, pct, rate, sev in r["alerts"]:
        out.append(f"  {lw:<5} {sw:<6} {pct:<7} {rate + '×':<10} {sev}")
    consumed = None
    if args.consumed_minutes is not None:
        consumed = Decimal(str(args.consumed_minutes)) / budget * 100
        basis = f"{args.consumed_minutes:g} min of {hms(budget)}"
    elif args.requests is not None:
        allowed = r["frac"] * Decimal(args.requests)
        consumed = Decimal(args.failed) / allowed * 100
        basis = f"{args.failed:,} failed of {allowed.normalize():,f} allowed ({args.requests:,} requests)"
    if consumed is not None:
        out += [
            "",
            f"Consumed: {q2(consumed)}% ({basis})",
            f"State:    {state(consumed)}   (HEALTHY < 50%, ERODING 50–100%, EXHAUSTED > 100%)",
        ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SLO error-budget arithmetic.")
    ap.add_argument("--slo", required=True, help="target in percent, e.g. 99.5")
    ap.add_argument("--window-days", type=int, default=28, help="rolling window (default 28)")
    used = ap.add_mutually_exclusive_group()
    used.add_argument("--consumed-minutes", type=float, help="bad minutes so far (time-based SLI)")
    used.add_argument("--requests", type=int, help="total eligible requests so far (request-based SLI)")
    ap.add_argument("--failed", type=int, help="failed requests so far (with --requests)")
    args = ap.parse_args(argv)
    try:
        try:
            slo = Decimal(args.slo)
        except Exception:
            raise InputError(f"--slo {args.slo!r} is not a number")
        if not Decimal(0) < slo < Decimal(100):
            raise InputError("--slo must be between 0 and 100 (exclusive), in percent")
        if args.window_days < 1:
            raise InputError("--window-days must be >= 1")
        if (args.requests is None) != (args.failed is None):
            raise InputError("--requests and --failed go together")
        if args.requests is not None and (args.requests < 1 or args.failed < 0):
            raise InputError("--requests must be >= 1 and --failed >= 0")
        if args.consumed_minutes is not None and args.consumed_minutes < 0:
            raise InputError("--consumed-minutes must be >= 0")
        print(render(args, slo, compute(slo, args.window_days)))
    except InputError as e:
        print(f"error-budget: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
