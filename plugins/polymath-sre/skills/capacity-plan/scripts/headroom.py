#!/usr/bin/env python3
"""headroom — demand growth fit, ceiling-crossing date, and must-act-by date.

  headroom.py --history 41,43,44,46,49,51 --period month --capacity 100 \
      --ceiling 0.7 --lead-time-days 42 --as-of 2026-10-26 [--event 2026-11-27:2.5]

  headroom.py --current 51 --growth 4% --period month --capacity 100 \
      --ceiling 0.7 --lead-time-days 42 --as-of 2026-10-26

--history is the driver/utilization per period, oldest first, in the same unit
as --capacity. Both models are fitted by least squares — linear (y = a + b·t)
and compound (ln y = a + b·t) — and compared by R² in the original units;
`--model auto` picks the higher R² (a tie picks compound: it breaches sooner).
Projection starts from the LAST observed value, so a poor fit cannot move "now".

--growth without history: `4%` = compound per period, `+2` = linear per period.
--event DATE:MULT applies a multiplier to the projected value on that date
(a launch, a sale). Several --event flags are allowed.

Breach = projected demand ≥ ceiling × capacity. Must-act-by = earliest breach −
lead time. --as-of is required so the same inputs always give the same dates.

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import sys

PERIOD_DAYS = {"day": 1.0, "week": 7.0, "month": 365.25 / 12, "quarter": 365.25 / 4}


class InputError(Exception):
    pass


def lstsq(ts: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(ts)
    mt, my = sum(ts) / n, sum(ys) / n
    sxx = sum((t - mt) ** 2 for t in ts)
    b = sum((t - mt) * (y - my) for t, y in zip(ts, ys)) / sxx
    return my - b * mt, b


def r2(ys: list[float], preds: list[float]) -> float:
    my = sum(ys) / len(ys)
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum((y - p) ** 2 for y, p in zip(ys, preds))
    return 1.0 if sst == 0 else 1 - sse / sst


def fit(history: list[float]) -> dict:
    ts = list(range(len(history)))
    a, b = lstsq(ts, history)
    lin = {"model": "linear", "rate": b, "r2": r2(history, [a + b * t for t in ts])}
    if min(history) <= 0:
        return {"linear": lin, "compound": None}
    la, lb = lstsq(ts, [math.log(y) for y in history])
    comp = {"model": "compound", "rate": math.exp(lb) - 1,
            "r2": r2(history, [math.exp(la + lb * t) for t in ts])}
    return {"linear": lin, "compound": comp}


def project(model: str, rate: float, current: float, periods: float) -> float:
    if model == "linear":
        return current + rate * periods
    return current * (1 + rate) ** periods


def periods_to(model: str, rate: float, current: float, target: float) -> float | None:
    if current >= target:
        return 0.0
    if model == "linear":
        return (target - current) / rate if rate > 0 else None
    return math.log(target / current) / math.log(1 + rate) if rate > 0 else None


def parse_growth(text: str) -> tuple[str, float]:
    t = text.strip()
    try:
        if t.endswith("%"):
            return "compound", float(t[:-1]) / 100
        return "linear", float(t)
    except ValueError:
        raise InputError("--growth is `4%` (compound per period) or `+2` (linear per period)")


def parse_event(text: str) -> tuple[dt.date, float]:
    try:
        d, m = text.split(":")
        return dt.date.fromisoformat(d), float(m.lstrip("x×"))
    except ValueError:
        raise InputError(f"--event {text!r}: use YYYY-MM-DD:MULTIPLIER, e.g. 2026-11-27:2.5")


def fmt_rate(model: str, rate: float, period: str) -> str:
    return f"{rate:+.2f}/{period}" if model == "linear" else f"{rate * 100:+.2f}%/{period}"


def run(args) -> str:
    try:
        as_of = dt.date.fromisoformat(args.as_of)
    except ValueError:
        raise InputError("--as-of must be YYYY-MM-DD")
    if not 0 < args.ceiling <= 1:
        raise InputError("--ceiling is a fraction of capacity in (0, 1], e.g. 0.7")
    if args.capacity <= 0 or args.lead_time_days < 0:
        raise InputError("--capacity must be > 0 and --lead-time-days >= 0")
    target = args.ceiling * args.capacity
    pdays = PERIOD_DAYS[args.period]
    out = [f"Headroom forecast (as of {as_of})"]

    if args.history:
        try:
            hist = [float(x) for x in args.history.split(",") if x.strip()]
        except ValueError:
            raise InputError("--history must be comma-separated numbers")
        if len(hist) < 3:
            raise InputError("--history needs at least 3 periods to fit a trend")
        if min(hist) < 0:
            raise InputError("--history values must be >= 0")
        fits = fit(hist)
        current = hist[-1]
        cand = [f for f in (fits["linear"], fits["compound"]) if f]
        if args.model == "auto":
            chosen = max(cand, key=lambda f: (round(f["r2"], 6), f["model"] == "compound"))
        else:
            chosen = fits[args.model]
            if chosen is None:
                raise InputError("compound fit needs every history value > 0")
        model, rate = chosen["model"], chosen["rate"]
        out.append(f"History:   {len(hist)} {args.period}s: {','.join(f'{h:g}' for h in hist)}  (oldest first)")
        tie = len(cand) == 2 and round(cand[0]["r2"], 6) == round(cand[1]["r2"], 6)
        why = "(--model)" if args.model != "auto" else ("(R² tie → compound, breaches sooner)" if tie else "(higher R²)")
        for i, f in enumerate(cand):
            label = "Fit:      " if i == 0 else "          "
            mark = f"   ← chosen {why}" if f is chosen else ""
            out.append(f"{label} {f['model']:<9}{fmt_rate(f['model'], f['rate'], args.period):<16}R² {f['r2']:.3f}{mark}")
    else:
        if args.current is None or args.growth is None:
            raise InputError("give --history, or both --current and --growth")
        model, rate = parse_growth(args.growth)
        current = args.current
        out.append(f"Growth:    {model} {fmt_rate(model, rate, args.period)} (stated, not fitted — label it an assumption)")

    out += [
        f"Ceiling:   {target:g} ({args.ceiling:.0%} of capacity {args.capacity:g})",
        f"Now:       {current:g} ({current / target:.0%} of ceiling)",
    ]
    breaches: list[tuple[dt.date, str]] = []
    p = periods_to(model, rate, current, target)
    if p == 0:
        out.append("Trend:     ALREADY AT/ABOVE CEILING")
        breaches.append((as_of, "already above ceiling"))
    elif p is None:
        out.append("Trend:     flat or shrinking — no trend breach")
    else:
        d = as_of + dt.timedelta(days=math.floor(p * pdays))
        out.append(f"Trend:     breach in {p:.1f} {args.period}s → {d}")
        breaches.append((d, "trend"))
    for ev in args.event or []:
        ed, mult = parse_event(ev)
        if ed < as_of:
            raise InputError(f"--event {ed} is before --as-of {as_of}")
        val = project(model, rate, current, (ed - as_of).days / pdays) * mult
        hit = val >= target
        out.append(f"Event:     {ed} ×{mult:g} → projected {val:.1f}" + ("  BREACH" if hit else f"  ok ({val / target:.1%} of ceiling)"))
        if hit:
            breaches.append((ed, f"event {ed}"))
    out.append(f"Lead time: {args.lead_time_days} days")
    if breaches:
        first, why = min(breaches)
        act = first - dt.timedelta(days=args.lead_time_days)
        late = "  ← already past: act now" if act <= as_of else ""
        out.append(f"Must act by: {act} (first breach {first}, {why}){late}")
    else:
        out.append("Must act by: no breach projected — re-run when the trend changes")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Growth fit + headroom + must-act-by date.")
    ap.add_argument("--history", help="per-period values, oldest first: 41,43,44,46")
    ap.add_argument("--current", type=float, help="current value (with --growth, no history)")
    ap.add_argument("--growth", help="4%% compound or +2 linear, per period (no history)")
    ap.add_argument("--model", choices=["auto", "linear", "compound"], default="auto")
    ap.add_argument("--period", choices=sorted(PERIOD_DAYS), default="month")
    ap.add_argument("--capacity", type=float, required=True, help="max of the constrained resource, same unit")
    ap.add_argument("--ceiling", type=float, default=0.7, help="safe utilization fraction (default 0.7)")
    ap.add_argument("--lead-time-days", type=int, required=True, help="provisioning lead time")
    ap.add_argument("--as-of", required=True, help="date of the last observation, YYYY-MM-DD")
    ap.add_argument("--event", action="append", help="YYYY-MM-DD:MULTIPLIER (repeatable)")
    args = ap.parse_args(argv)
    try:
        print(run(args))
    except InputError as e:
        print(f"headroom: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
