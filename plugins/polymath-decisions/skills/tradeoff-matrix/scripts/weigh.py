#!/usr/bin/env python3
"""weigh — weighted tradeoff matrix with the full ±1 sensitivity sweep.

Reads a CSV on stdin (or --file); one row per criterion, one column per option:

    criterion,weight,A. In-memory,B. Redis,C. Postgres
    Latency (P99),5,5,5,3
    Operational burden,4,5,3,4

Weights and scores are integers 1–5. Append `?` to a guessed score (`4?`).

Prints, in a fixed order:
  1. the options × criteria table with the math per cell (`w × s = v`) and totals
  2. the ranking
  3. criteria that do not differentiate (every option scores the same)
  4. the sensitivity sweep: every weight ±1 and every score ±1 (clamped to 1–5)
     that changes the sole winner — or the line "no single ±1 change flips the
     winner". A guessed score that flips the winner is called out.

Exit 0 ok, 2 bad input.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys

LO, HI = 1, 5


class InputError(Exception):
    pass


def cell(raw: str, where: str) -> tuple[int, bool]:
    raw = (raw or "").strip()
    guess = raw.endswith("?")
    try:
        v = int(raw.rstrip("?").strip())
    except ValueError:
        raise InputError(f"{where}: {raw!r} is not a whole number 1–5")
    if not LO <= v <= HI:
        raise InputError(f"{where}: {v} is outside 1–5")
    return v, guess


def parse(text: str) -> tuple[list[str], list[dict]]:
    rows = list(csv.reader(io.StringIO(text.strip())))
    if len(rows) < 3:
        raise InputError("need a header row and at least two criteria")
    header = [h.strip() for h in rows[0]]
    if [h.lower() for h in header[:2]] != ["criterion", "weight"] or len(header) < 4:
        raise InputError("header must be `criterion,weight,<option>,<option>[,…]` (at least two options)")
    options = header[2:]
    if len(set(options)) != len(options):
        raise InputError("option names must be unique")
    criteria = []
    for row in rows[1:]:
        if not any(c.strip() for c in row):
            continue
        if len(row) != len(header):
            raise InputError(f"row {row[0]!r}: expected {len(header)} cells, got {len(row)}")
        name = row[0].strip()
        w, wg = cell(row[1], f"{name} / weight")
        if wg:
            raise InputError(f"{name}: a weight is a stated priority, not a guess — drop the `?`")
        scores, guesses = [], []
        for opt, raw in zip(options, row[2:]):
            s, g = cell(raw, f"{name} / {opt}")
            scores.append(s)
            guesses.append(g)
        criteria.append({"name": name, "weight": w, "scores": scores, "guesses": guesses})
    if len(criteria) < 2:
        raise InputError("need at least two criteria")
    return options, criteria


def totals(criteria: list[dict], n_opts: int) -> list[int]:
    return [sum(c["weight"] * c["scores"][i] for c in criteria) for i in range(n_opts)]


def sole_winner(tot: list[int]) -> int | None:
    best = max(tot)
    idx = [i for i, t in enumerate(tot) if t == best]
    return idx[0] if len(idx) == 1 else None


def sweep(options: list[str], criteria: list[dict]) -> list[tuple[str, str]]:
    """Every single ±1 change that alters the sole winner, as (criterion, line)."""
    base = sole_winner(totals(criteria, len(options)))
    flips: list[tuple[str, str]] = []

    def outcome(tot):
        w = sole_winner(tot)
        return "tie at the top" if w is None else f"{options[w]} wins"

    for ci, c in enumerate(criteria):
        for d in (-1, 1):
            nw = c["weight"] + d
            if not LO <= nw <= HI:
                continue
            trial = [dict(x, weight=nw) if k == ci else x for k, x in enumerate(criteria)]
            tot = totals(trial, len(options))
            if sole_winner(tot) != base:
                flips.append((c["name"], f"- weight of {c['name']} {c['weight']}→{nw}: {outcome(tot)}"))
        for oi, opt in enumerate(options):
            for d in (-1, 1):
                ns = c["scores"][oi] + d
                if not LO <= ns <= HI:
                    continue
                scores = list(c["scores"])
                scores[oi] = ns
                trial = [dict(x, scores=scores) if k == ci else x for k, x in enumerate(criteria)]
                tot = totals(trial, len(options))
                if sole_winner(tot) != base:
                    tag = " (GUESSED score)" if c["guesses"][oi] else ""
                    flips.append((c["name"], f"- {opt} on {c['name']} {c['scores'][oi]}→{ns}{tag}: {outcome(tot)}"))
    return flips


def render(options: list[str], criteria: list[dict]) -> str:
    tot = totals(criteria, len(options))
    head = ["Option"] + [f"{c['name']} (×{c['weight']})" for c in criteria] + ["**Total**"]
    out = ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)]
    for oi, opt in enumerate(options):
        cells = []
        for c in criteria:
            s = c["scores"][oi]
            mark = "?" if c["guesses"][oi] else ""
            cells.append(f"{s}{mark} × {c['weight']} = {s * c['weight']}")
        out.append("| " + " | ".join([opt] + cells + [f"**{tot[oi]}**"]) + " |")

    order = sorted(range(len(options)), key=lambda i: (-tot[i], i))
    out += ["", "Ranking:"]
    for r, i in enumerate(order, 1):
        out.append(f"  {r}. {options[i]} — {tot[i]}")
    w = sole_winner(tot)
    if w is None:
        out.append("  No sole winner: the top totals tie — the decision rests on the discussion, not the math.")

    flat = [c["name"] for c in criteria if len(set(c["scores"])) == 1]
    out += ["", "Non-differentiating criteria (a fact, not a criterion — re-cut or drop):"]
    out += [f"  - {n}" for n in flat] or ["  none"]

    flips = sweep(options, criteria)
    out += ["", "Sensitivity (every weight ±1, every score ±1, clamped to 1–5):"]
    if flips:
        out += [f"  {line}" for _, line in flips]
        hinge = [c["name"] for c in criteria if any(name == c["name"] for name, _ in flips)]
        out.append(f"  The decision hinges on: {', '.join(hinge)} — those weights/scores need evidence, not opinion.")
    else:
        out.append("  No single ±1 change flips the winner.")
    guessed = sum(g for c in criteria for g in c["guesses"])
    if guessed:
        out.append(f"  {guessed} guessed score(s) marked `?` in the table.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Weighted tradeoff matrix + ±1 sensitivity sweep.")
    ap.add_argument("--file", help="CSV file (default: stdin)")
    args = ap.parse_args(argv)
    try:
        text = open(args.file).read() if args.file else sys.stdin.read()
        print(render(*parse(text)))
    except (InputError, OSError) as e:
        print(f"weigh: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
