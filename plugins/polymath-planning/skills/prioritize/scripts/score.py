#!/usr/bin/env python3
"""score — RICE / WSJF prioritization with visible inputs and a fixed tie-break.

Reads a CSV on stdin (or --file). Append `?` to any input that is a guess
(`2000?`); guesses are carried into the output and stress-tested.

  RICE  columns: item,reach,impact,confidence,effort
        score = reach × impact × confidence / effort
        impact on the Intercom scale (0.25, 0.5, 1, 2, 3); confidence as 0–1
        or a percentage (80 → 0.8); effort in person-weeks (> 0).
  WSJF  columns: item,value,time_criticality,risk_reduction,job_size
        cost of delay = value + time_criticality + risk_reduction
        score = cost of delay / job_size

Ranking is by score descending; ties break by (RICE) higher confidence then
lower effort, (WSJF) higher cost of delay then smaller job — then input order.
A row whose score equals the row above is marked `=` (the tie-break set its place).

Sensitivity: for every row with a guessed input, each guess is re-scored at
×0.5 and ×2 (all others held); the row's best/worst rank is reported, so a
rank that only holds because of a guess is visible.

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys

COLUMNS = {
    "rice": ["reach", "impact", "confidence", "effort"],
    "wsjf": ["value", "time_criticality", "risk_reduction", "job_size"],
}
RICE_IMPACT = {0.25, 0.5, 1.0, 2.0, 3.0}


class InputError(Exception):
    pass


def num(cell: str, where: str) -> tuple[float, bool]:
    cell = (cell or "").strip()
    guess = cell.endswith("?")
    try:
        return float(cell.rstrip("?").strip()), guess
    except ValueError:
        raise InputError(f"{where}: {cell!r} is not a number (append ? to mark a guess, never leave it blank)")


def parse(text: str, method: str) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text.strip())))
    if not rows:
        raise InputError("no items: expected a CSV header row and at least one item")
    cols = COLUMNS[method]
    header = {k.strip().lower() for k in rows[0].keys()}
    missing = ({"item"} | set(cols)) - header
    if missing:
        raise InputError(f"{method.upper()} needs column(s): {', '.join(sorted(missing))}")
    items = []
    for i, raw in enumerate(rows, 1):
        r = {k.strip().lower(): v for k, v in raw.items()}
        name = (r["item"] or "").strip() or f"row {i}"
        vals, guesses = {}, set()
        for c in cols:
            vals[c], g = num(r[c], f"{name} / {c}")
            if g:
                guesses.add(c)
        if method == "rice":
            if vals["confidence"] > 1:
                vals["confidence"] /= 100
            if not 0 < vals["confidence"] <= 1:
                raise InputError(f"{name}: confidence must be in (0, 1] or (0, 100]")
            if vals["impact"] not in RICE_IMPACT:
                raise InputError(f"{name}: impact must be one of 0.25, 0.5, 1, 2, 3")
            if vals["effort"] <= 0 or vals["reach"] < 0:
                raise InputError(f"{name}: effort must be > 0 and reach >= 0")
        else:
            if vals["job_size"] <= 0 or min(vals[c] for c in cols[:3]) < 0:
                raise InputError(f"{name}: job_size must be > 0 and value/time/risk >= 0")
        items.append({"item": name, "vals": vals, "guesses": guesses, "order": i})
    return items


def score(method: str, v: dict) -> float:
    if method == "rice":
        return v["reach"] * v["impact"] * v["confidence"] / v["effort"]
    return (v["value"] + v["time_criticality"] + v["risk_reduction"]) / v["job_size"]


def sort_key(method: str, it: dict) -> tuple:
    v = it["vals"]
    s = round(score(method, v), 9)
    if method == "rice":
        return (-s, -v["confidence"], v["effort"], it["order"])
    cod = v["value"] + v["time_criticality"] + v["risk_reduction"]
    return (-s, -cod, v["job_size"], it["order"])


def rank_of(method: str, items: list[dict], target: dict, override: dict) -> int:
    trial = [dict(it, vals=dict(it["vals"], **override)) if it is target else it for it in items]
    ordered = sorted(trial, key=lambda it: sort_key(method, it))
    return next(i for i, it in enumerate(ordered, 1) if it["order"] == target["order"])


def fmt(x: float) -> str:
    return f"{x:,.2f}".rstrip("0").rstrip(".") if x != int(x) else f"{int(x):,}"


def render(method: str, items: list[dict]) -> str:
    ordered = sorted(items, key=lambda it: sort_key(method, it))
    cols = COLUMNS[method]
    head = ["Rank", "Item"] + cols + (["score"] if method == "rice" else ["cost_of_delay", "wsjf"])
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    prev = None
    for rank, it in enumerate(ordered, 1):
        v = it["vals"]
        s = round(score(method, v), 9)
        tie = "=" if prev is not None and s == prev else ""
        prev = s
        cells = []
        for c in cols:
            shown = f"{v[c]:.0%}" if (method == "rice" and c == "confidence") else fmt(v[c])
            cells.append(shown + ("?" if c in it["guesses"] else ""))
        tail = [fmt(score(method, v))]
        if method == "wsjf":
            tail = [fmt(v["value"] + v["time_criticality"] + v["risk_reduction"]), fmt(score(method, v))]
        lines.append("| " + " | ".join([f"{rank}{tie}", it["item"]] + cells + tail) + " |")

    notes = []
    for it in ordered:
        if method == "rice" and it["vals"]["confidence"] <= 0.5:
            notes.append(f"- LOW CONFIDENCE ({it['vals']['confidence']:.0%}): {it['item']} — rank rests on speculation.")
    for it in ordered:
        if not it["guesses"]:
            continue
        base = rank_of(method, items, it, {})
        ranks = [base]
        for g in sorted(it["guesses"]):
            for factor in (0.5, 2.0):
                ranks.append(rank_of(method, items, it, {g: it["vals"][g] * factor}))
        lo, hi = min(ranks), max(ranks)
        guessed = ", ".join(sorted(it["guesses"]))
        if lo == hi:
            notes.append(f"- {it['item']}: guessed {guessed}; rank {base} holds at ×0.5 / ×2.")
        else:
            notes.append(f"- {it['item']}: guessed {guessed}; rank moves {lo}–{hi} at ×0.5 / ×2 — needs evidence before it is committed.")
    out = [f"Method: {method.upper()}  ({len(items)} items; `?` = guessed input; `=` = same score as the row above, order set by the tie-break)", ""] + lines
    if notes:
        out += ["", "Flags:"] + notes
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RICE / WSJF scoring with visible inputs.")
    ap.add_argument("--method", choices=sorted(COLUMNS), required=True)
    ap.add_argument("--file", help="CSV file (default: stdin)")
    args = ap.parse_args(argv)
    try:
        text = open(args.file).read() if args.file else sys.stdin.read()
        print(render(args.method, parse(text, args.method)))
    except (InputError, OSError) as e:
        print(f"score: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
