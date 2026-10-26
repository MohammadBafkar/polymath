#!/usr/bin/env python3
"""pert — three-point (PERT-style) estimate aggregation, computed exactly.

Reads a CSV on stdin (or --file) with a header row:

    step,o,e,p[,critical]

o / e / p are the optimistic (10th pct), expected (50th) and pessimistic (90th)
hours; append `?` to a number the team has not confirmed (`4?`). `critical` is
y/n (default y) — only critical-path steps add to the total.

Per step:   mean = (O + 4E + P) / 6      sigma = (P - O) / 2.56
Total:      mean = sum of critical means sigma = sqrt(sum of critical sigma^2)
80% range:  mean +/- 1.28 * sigma         (floored at 0)

Flags any step with P / O > 3 (poorly scoped: decompose before estimating).
Converts hours to working days with --focus-hours (default 5 focus hours/day).

Exit 0 ok, 2 bad input. Output is the fixed table the estimate skill shows.
"""

from __future__ import annotations

import argparse
import csv
import io
import math
import sys

Z80 = 1.28
SIGMA_DIVISOR = 2.56  # O and P are the 10th / 90th percentiles


class InputError(Exception):
    pass


def parse(text: str) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text.strip())))
    if not rows:
        raise InputError("no steps: expected a CSV header `step,o,e,p[,critical]` and at least one row")
    missing = {"step", "o", "e", "p"} - {k.strip().lower() for k in rows[0].keys()}
    if missing:
        raise InputError(f"missing column(s): {', '.join(sorted(missing))}")
    steps = []
    for i, raw in enumerate(rows, 1):
        r = {k.strip().lower(): (v or "").strip() for k, v in raw.items()}
        draft = any(r[k].endswith("?") for k in ("o", "e", "p"))
        try:
            o, e, p = (float(r[k].rstrip("?").strip()) for k in ("o", "e", "p"))
        except ValueError:
            raise InputError(f"row {i} ({r['step']!r}): o/e/p must be numbers (append ? to mark a draft)")
        if o < 0 or not (o <= e <= p):
            raise InputError(f"row {i} ({r['step']!r}): need 0 <= O <= E <= P, got {o}/{e}/{p}")
        crit = r.get("critical", "y").lower() not in ("n", "no", "false", "0")
        steps.append({"step": r["step"], "o": o, "e": e, "p": p, "critical": crit, "draft": draft})
    return steps


def compute(steps: list[dict], focus_hours: float) -> dict:
    for s in steps:
        s["mean"] = (s["o"] + 4 * s["e"] + s["p"]) / 6
        s["sigma"] = (s["p"] - s["o"]) / SIGMA_DIVISOR
        s["decompose"] = s["o"] == 0 or s["p"] / s["o"] > 3
    crit = [s for s in steps if s["critical"]]
    mean = sum(s["mean"] for s in crit)
    sigma = math.sqrt(sum(s["sigma"] ** 2 for s in crit))
    return {
        "steps": steps,
        "mean": mean,
        "sigma": sigma,
        "low": max(0.0, mean - Z80 * sigma),
        "high": mean + Z80 * sigma,
        "focus_hours": focus_hours,
    }


def fmt(x: float) -> str:
    return f"{x:.1f}"


def render(res: dict, goal: str) -> str:
    steps = res["steps"]
    width = max(20, max(len(s["step"]) for s in steps) + 4)
    drafts = sum(s["draft"] for s in steps)
    title = f"Estimate: {goal}" + ("   DRAFT — numbers not confirmed by the team" if drafts else "")
    out = [title, "", "Per-step (hours):"]
    out.append(f"  {'Step':<{width}}{'O':>6}{'E':>6}{'P':>6}{'Mean':>8}{'σ':>7}")
    for i, s in enumerate(steps, 1):
        name = f"{i}. {s['step']}"
        notes = []
        if not s["critical"]:
            notes.append("off critical path")
        if s["decompose"]:
            notes.append("P/O > 3, decompose")
        if s["draft"]:
            notes.append("draft")
        note = f"   ← {'; '.join(notes)}" if notes else ""
        out.append(
            f"  {name:<{width}}{s['o']:>6g}{s['e']:>6g}{s['p']:>6g}"
            f"{fmt(s['mean']):>8}{fmt(s['sigma']):>7}{note}"
        )
    fh = res["focus_hours"]
    days = lambda h: fmt(h / fh)  # noqa: E731
    out += [
        "",
        f"Critical path mean: {fmt(res['mean'])} h ≈ {days(res['mean'])} working days at {fh:g} focus h/day",
        f"80% interval: {fmt(res['low'])} .. {fmt(res['high'])} h  "
        f"({days(res['low'])} .. {days(res['high'])} days; σ_total = {fmt(res['sigma'])} h, "
        "independent steps — correlated risks widen it)",
    ]
    flagged = [s["step"] for s in steps if s["decompose"]]
    if flagged:
        out.append(f"Decompose before committing: {', '.join(flagged)}")
    if drafts:
        out.append(f"Drafted numbers: {drafts} of {len(steps)} steps — confirm with the team before quoting.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Aggregate three-point estimates exactly.")
    ap.add_argument("--file", help="CSV file (default: stdin)")
    ap.add_argument("--goal", default="<goal>", help="goal name for the header line")
    ap.add_argument("--focus-hours", type=float, default=5.0,
                    help="team focus hours per working day (default 5; never assume 8)")
    args = ap.parse_args(argv)
    try:
        text = open(args.file).read() if args.file else sys.stdin.read()
        if args.focus_hours <= 0:
            raise InputError("--focus-hours must be > 0")
        print(render(compute(parse(text), args.focus_hours), args.goal))
    except (InputError, OSError) as e:
        print(f"pert: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
