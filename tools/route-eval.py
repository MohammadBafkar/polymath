#!/usr/bin/env python3
"""Held-out routing measurement (Claim A: does the deterministic router fire correctly?).

This is NOT tests/route-triggering/*.md. Those fixtures are green by construction
(authored to pass, wired into conformance as a gate). This is a HELD-OUT eval:
naturalistic prompts written the way a user actually phrases a task, NOT
reverse-engineered from the signal table, plus deliberately-signalled prompts to
measure precision and adversarial negatives to measure false positives.

It is a MEASUREMENT, not a gate. It always exits 0 and is not wired into
conformance. Its only job is to produce honest numbers about the route-hint hook
(plugins/polymath-core/hooks/scripts/route-hint.py) -- including misses.

Categories (tests/route-eval/heldout.jsonl):
  naturalistic  Plain-English task. Measures REACH: how often the hard-signal
                router fires at all on natural phrasing. Non-firing is BY DESIGN
                (the router requires a hard signal), so it is reported, not failed.
  token         A hard signal (url / cve / path+intent) is deliberately present.
                Measures PRECISION: fire AND route to the right surface.
  negative      Should stay silent. Measures the FALSE-POSITIVE rate.
  ambiguous     Two surfaces compete. Reports the top candidate and whether the
                expected surface appears; the observation is the result.

Run: python3 tools/route-eval.py [--json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOOK = ROOT / "plugins" / "polymath-core" / "hooks" / "scripts" / "route-hint.py"
CASES = ROOT / "tests" / "route-eval" / "heldout.jsonl"
FIRED_MARKER = "[polymath-core route]"
# A candidate line: "  - <surface>  (<kind> -- <why>)". Surface ends at the 2-space gap.
CAND_RE = re.compile(r"^\s+-\s+(.+?)\s{2,}\(", re.MULTILINE)


def run_hook(prompt: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"prompt": prompt}),
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.stdout


def candidates(out: str) -> list[str]:
    return [m.strip() for m in CAND_RE.findall(out)]


def load_cases() -> list[dict]:
    rows = []
    for line in CASES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def classify(case: dict, fired: bool, cands: list[str]) -> str:
    top = cands[0] if cands else ""
    target = case.get("target", "")
    hit = bool(target) and any(target in c for c in cands)
    top_hit = bool(target) and target in top
    cat = case["category"]
    if cat == "negative":
        return "FALSE-POSITIVE" if fired else "ok-silent"
    if cat == "naturalistic":
        if case["expect"] == "silent":
            # Silence is the by-design outcome; firing on pure prose is the surprise.
            return "fired-unexpected" if fired else "silent-by-design"
        # expect == fire (incidental-token case): score like a token case.
        if not fired:
            return "MISS"
        return "ok-top" if top_hit else ("ok-listed" if hit else "MISROUTE")
    if cat == "token":
        if not fired:
            return "MISS"
        return "ok-top" if top_hit else ("ok-listed" if hit else "MISROUTE")
    if cat == "ambiguous":
        if not fired:
            return "amb-MISS"
        return "amb-top" if top_hit else ("amb-listed" if hit else "amb-other")
    return "?"


def main() -> int:
    ap = argparse.ArgumentParser(description="Held-out routing measurement (no model, no token).")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    cases = load_cases()
    results = []
    for c in cases:
        out = run_hook(c["prompt"])
        fired = FIRED_MARKER in out
        cands = candidates(out)
        verdict = classify(c, fired, cands)
        results.append({
            "id": c["id"], "category": c["category"], "expect": c["expect"],
            "fired": fired, "top": cands[0] if cands else "", "candidates": cands,
            "target": c.get("target", ""), "verdict": verdict, "note": c.get("note", ""),
        })

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    # ---- human report -------------------------------------------------------
    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    print("HELD-OUT ROUTING MEASUREMENT  (deterministic; no model, no token)")
    print(f"cases: {len(results)}   hook: {HOOK.relative_to(ROOT)}\n")
    for cat in ("token", "ambiguous", "naturalistic", "negative"):
        rows = by_cat.get(cat, [])
        if not rows:
            continue
        print(f"== {cat} ({len(rows)}) ==")
        for r in rows:
            top = r["top"] or "(silent)"
            print(f"  {r['verdict']:<16} {r['id']:<24} -> {top}")
        print()

    # ---- aggregate metrics --------------------------------------------------
    def n(cat, *verdicts):
        return sum(1 for r in by_cat.get(cat, []) if r["verdict"] in verdicts)

    tok = by_cat.get("token", [])
    tok_fire = sum(1 for r in tok if r["fired"])
    tok_correct = n("token", "ok-top", "ok-listed")
    tok_misroute = n("token", "MISROUTE")
    tok_miss = n("token", "MISS")

    nat = by_cat.get("naturalistic", [])
    nat_total = len(nat)
    nat_fired = sum(1 for r in nat if r["fired"])

    neg = by_cat.get("negative", [])
    neg_fp = n("negative", "FALSE-POSITIVE")

    print("== SUMMARY ==")
    if tok:
        print(f"  token precision (fired -> correct surface): {tok_correct}/{tok_fire} fired, "
              f"{tok_miss} silent miss, {tok_misroute} misroute  (of {len(tok)} signalled prompts)")
    if nat:
        print(f"  naturalistic reach (fired at all):           {nat_fired}/{nat_total}  "
              f"-- the rest stay silent by design (no hard signal in natural phrasing)")
    if neg:
        print(f"  false-positive rate on negatives:            {neg_fp}/{len(neg)}")
    print()
    print("  Interpretation: precision/false-positives bound whether a hint, WHEN shown,")
    print("  is trustworthy. Reach bounds how OFTEN a hint appears on real phrasing. Neither")
    print("  measures whether narrowing 149->3 improves the MODEL's pick -- that is Claim B,")
    print("  which needs a live token.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
