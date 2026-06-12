#!/usr/bin/env python3
"""Build the model-facing workflow routing index from workflow YAML triggers.

Workflows are invisible to the model at runtime: unlike skills, their
descriptions never reach context, so the agent cannot propose a workflow it was
not explicitly told to run. This builder is the SINGLE PRODUCER of a compact,
token-budgeted index derived from each workflow's `whenToUse` / `triggers` /
`detectionSignals`. The polymath-flows SessionStart hook injects the *min*
index so the model can detect a match and propose it (see the propose/confirm
contract in plugins/polymath-flows/skills/run-workflow/SKILL.md).

Three outputs under plugins/polymath-flows/data/:
  workflow-index.json      FULL — [{n, w, t}]  (propose step + doctor)
  workflow-index.min.json  INJECTED — [{n, w}] (SessionStart, ~token-budgeted)
  workflow-detect.json     SIGNALS — [{n, paths, intents}] (non-injected)

Modes:
  (default)   build and write the three files.
  --check     build in memory and diff against what's on disk; exit 1 on drift
              (the conformance diff-guard — keeps the index from going stale).

The injection is TIERED: Tier A (repo-relevant first, alphabetical fill) is
budgeted at ≤ TIER_A_BUDGET tokens for the whole rendered block; the rest
collapse to the one-line Tier B pointer. Each whenToUse is capped at
WHEN_TO_USE_MAX_CHARS so no single workflow eats the shared block. This file
owns the budget constants; the renderer mirrors them (pinned by unit test).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - CI always has PyYAML
    print("build-workflow-index: PyYAML is required", file=sys.stderr)
    sys.exit(2)

REPO = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO / "plugins" / "polymath-flows" / "workflows"
DATA_DIR = REPO / "plugins" / "polymath-flows" / "data"

# Injection framing + tier constants — kept byte-identical to the SessionStart
# renderer (plugins/polymath-flows/hooks/scripts/project-index.py); a unit test
# pins the two files' constants and tier selection equal. The machine-local
# project fragment that renderer may append is deliberately OUTSIDE the budget.
INJECTION_HEADER = "Polymath workflows available (multi-step arcs you can run):"
INJECTION_FOOTER = (
    "Before starting substantial multi-step work that matches one of these, first "
    "propose that workflow in one line (name in backticks) and wait for approval; "
    "otherwise just answer. Never start a workflow without asking."
)
# Tiered injection: Tier A (full `name: whenToUse` lines, repo-relevant first,
# alphabetical fill) is budgeted at ≤ TIER_A_BUDGET tokens for the whole
# catalog block — header, entries, pointer, footer. Everything else collapses
# to the one-line Tier B pointer. This replaces the old flat-list ceiling
# (which had reached its cap with zero headroom): growth lands in Tier B,
# never in always-on tokens. THIS BUILDER IS THE ONE BUDGET OWNER — catalog,
# project, and pack layers all render through the same constants.
TIER_A_BUDGET = 400
# No single workflow may eat the shared block: whenToUse is capped per entry.
WHEN_TO_USE_MAX_CHARS = 140
TIER_B_POINTER = (
    "  …plus {n} more — full list: polymath-flows data/workflow-index.json; "
    "ask /polymath-core:route to pick."
)


def estimate_tokens(text: str) -> int:
    # (chars + 3) // 4 — tools/lib/tokens.py's arithmetic; deterministic in
    # every environment (the old tiktoken-when-available path made the budget
    # depend on what happened to be importable).
    return (len(text) + 3) // 4


def select_tier_a(min_records: list[dict], relevant: set[str]) -> tuple[list[dict], list[dict]]:
    """Deterministic tier split: repo-relevant records first (alphabetical),
    then the rest (alphabetical), greedily admitted while the rendered block
    — header + entries + worst-case pointer + footer — stays ≤ TIER_A_BUDGET.
    Returns (tier_a, tier_b)."""
    ordered = sorted(min_records, key=lambda r: (r["n"] not in relevant, r["n"]))
    overhead = (
        estimate_tokens(INJECTION_HEADER)
        + estimate_tokens(TIER_B_POINTER.format(n=len(min_records)))
        + estimate_tokens(INJECTION_FOOTER)
    )
    tier_a: list[dict] = []
    used = overhead
    for rec in ordered:
        cost = estimate_tokens(f"  - {rec['n']}: {rec['w']}")
        if used + cost > TIER_A_BUDGET:
            break  # deterministic cut; remaining records all go to Tier B
        tier_a.append(rec)
        used += cost
    tier_a_names = {r["n"] for r in tier_a}
    tier_b = [r for r in min_records if r["n"] not in tier_a_names]
    return tier_a, tier_b


def render_injection(min_records: list[dict], relevant: set[str] | None = None) -> str:
    tier_a, tier_b = select_tier_a(min_records, relevant or set())
    lines = [INJECTION_HEADER]
    lines += [f"  - {r['n']}: {r['w']}" for r in tier_a]
    if tier_b:
        lines.append(TIER_B_POINTER.format(n=len(tier_b)))
    lines.append(INJECTION_FOOTER)
    return "\n".join(lines)


def collect() -> tuple[list[dict], list[dict], list[dict], dict]:
    full, mini, detect = [], [], []
    duplicates: list[str] = []
    no_routing: list[str] = []
    seen_triggers: dict[str, str] = {}
    all_names: set[str] = set()
    chain_decls: list[tuple[str, str]] = []

    for path in sorted(WORKFLOWS_DIR.glob("*.yaml")):
        wf = yaml.safe_load(path.read_text()) or {}
        name = wf.get("name")
        when = wf.get("whenToUse")
        triggers = wf.get("triggers") or []
        signals = wf.get("detectionSignals") or {}
        if not name:
            continue
        all_names.add(name)
        for c in wf.get("chainsTo") or []:
            chain_decls.append((name, c))
        if not when or not triggers:
            no_routing.append(name)
            continue
        full.append({"n": name, "w": when, "t": list(triggers)})
        mini.append({"n": name, "w": when})
        rec = {"n": name}
        if signals.get("paths"):
            rec["paths"] = list(signals["paths"])
        if signals.get("intents"):
            rec["intents"] = list(signals["intents"])
        detect.append(rec)
        for t in triggers:
            if t in seen_triggers:
                duplicates.append(f"trigger {t!r} in both {name} and {seen_triggers[t]}")
            seen_triggers[t] = name

    full.sort(key=lambda r: r["n"])
    mini.sort(key=lambda r: r["n"])
    detect.sort(key=lambda r: r["n"])
    dangling = sorted(
        f"chainsTo {t!r} in {w} is not a known workflow"
        for (w, t) in chain_decls
        if t not in all_names
    )
    return full, mini, detect, {
        "no_routing": sorted(no_routing),
        "duplicates": duplicates,
        "dangling_chains": dangling,
    }


def serialize(full: list[dict], mini: list[dict], detect: list[dict]) -> dict[str, str]:
    return {
        "workflow-index.json": json.dumps(full, indent=2, ensure_ascii=False) + "\n",
        "workflow-index.min.json": json.dumps(
            mini, separators=(",", ":"), ensure_ascii=False
        )
        + "\n",
        "workflow-detect.json": json.dumps(detect, indent=2, ensure_ascii=False) + "\n",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify on-disk files match a fresh build; exit 1 on drift",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="WORKFLOW-2: every workflow must declare whenToUse + triggers and "
        "no trigger may be shared across workflows; exit 1 on violation",
    )
    args = ap.parse_args()

    full, mini, detect, problems = collect()
    # WORKFLOW-2 enforcement (required routing surface + global trigger uniqueness).
    if args.strict:
        strict_errs = []
        if problems["no_routing"]:
            strict_errs.append(
                "missing whenToUse/triggers: " + ", ".join(problems["no_routing"])
            )
        strict_errs.extend(problems["duplicates"])
        strict_errs.extend(problems["dangling_chains"])
        if strict_errs:
            for e in strict_errs:
                print(f"build-workflow-index: WORKFLOW-2: {e}", file=sys.stderr)
            return 1
    else:
        # Grace mode: report the same issues as warnings without failing.
        for w in problems["no_routing"]:
            print(f"build-workflow-index: warning: {w} has no whenToUse/triggers (not indexed)", file=sys.stderr)
        for d in problems["duplicates"]:
            print(f"build-workflow-index: warning: duplicate {d}", file=sys.stderr)
        for d in problems["dangling_chains"]:
            print(f"build-workflow-index: warning: {d}", file=sys.stderr)

    # Per-entry cap: one workflow must not eat the shared Tier A block.
    over_cap = [r for r in mini if len(r["w"]) > WHEN_TO_USE_MAX_CHARS]
    if over_cap:
        for r in over_cap:
            print(
                f"build-workflow-index: whenToUse of {r['n']} is {len(r['w'])} chars "
                f"(cap {WHEN_TO_USE_MAX_CHARS}) — trim it",
                file=sys.stderr,
            )
        return 1
    # Tier budget: the rendered block self-truncates to TIER_A_BUDGET by
    # construction; assert the invariant holds in the worst case (every
    # workflow relevant) and report the split.
    rendered = render_injection(mini, relevant={r["n"] for r in mini})
    tokens = estimate_tokens(rendered)
    tier_a, tier_b = select_tier_a(mini, {r["n"] for r in mini})
    if tokens > TIER_A_BUDGET:
        print(
            f"build-workflow-index: tiered render is ~{tokens} tokens "
            f"(>{TIER_A_BUDGET}) — select_tier_a violated its own budget",
            file=sys.stderr,
        )
        return 1

    files = serialize(full, mini, detect)

    if args.check:
        drift = []
        for fname, content in files.items():
            disk = DATA_DIR / fname
            if not disk.exists() or disk.read_text() != content:
                drift.append(fname)
        if drift:
            print(
                "build-workflow-index: stale (run tools/build-workflow-index.py): "
                + ", ".join(drift),
                file=sys.stderr,
            )
            return 1
        print(
            f"workflow-index OK ({len(mini)} workflows; tier A {len(tier_a)}, "
            f"tier B {len(tier_b)} via pointer; ~{tokens} worst-case injection tokens)"
        )
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for fname, content in files.items():
        (DATA_DIR / fname).write_text(content)
    print(
        f"wrote {len(files)} index files for {len(mini)} workflows "
        f"(tier A {len(tier_a)} / tier B {len(tier_b)}; ~{tokens} worst-case injection tokens) "
        f"to {DATA_DIR.relative_to(REPO)}/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
