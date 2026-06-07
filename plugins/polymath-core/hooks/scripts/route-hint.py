#!/usr/bin/env python3
"""polymath-core UserPromptSubmit ambient routing hint.

Reads the user's prompt from a Claude Code hook payload on stdin, extracts
*deterministic* signals (URLs, ticket/CVE keys, file paths mentioned in the
prompt, inline diffs, intent phrasings), scores them against the bundled
``data/route-signals.json`` table, and — only when a HARD signal is present —
prints one quiet line proposing the smallest Polymath surface that fits.

Design contract (matches docs/plans/consolidation-and-dispatch.md, Layer 3):

* Detect -> propose -> confirm. NEVER auto-run anything.
* Hard signal required. Intent phrasings alone never fire (keeps false
  positives near zero); a URL / regex key / mentioned path / inline diff must
  contribute before a hint is emitted.
* Quiet by default. No signal -> no output -> exit 0.
* Suppressible. ``POLYMATH_ROUTE_MUTE=1`` or a ``.polymath/route-muted`` marker
  anywhere up the tree silences it.
* Degrade quiet. Any error -> exit 0 with no output. A hint must never break a
  turn.

The model is reliable at picking 1-of-3 and unreliable at 1-of-131; this hook's
only job is to do the narrowing the model can't, then get out of the way.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HARD_KINDS = ("url", "regex", "path", "diff")
SCORE = {"url": 3, "regex": 3, "path": 2, "diff": 2, "intent": 1}
MIN_SCORE = 3          # best candidate must clear this to emit
MAX_CANDIDATES = 3     # never show the user more than a 1-of-3 choice

DIFF_RE = re.compile(r"(?m)^(?:diff --git |@@ .*@@|\+\+\+ |--- |index [0-9a-f]{7,})")
URL_RE = re.compile(r"https?://[^\s)>\]\"']+")


def read_prompt() -> str:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return ""
    if not isinstance(data, dict):
        return ""
    return (data.get("prompt") or "").strip()


def muted() -> bool:
    if os.environ.get("POLYMATH_ROUTE_MUTE"):
        return True
    here = Path.cwd()
    for d in (here, *here.parents):
        if (d / ".polymath" / "route-muted").exists():
            return True
        if (d / ".git").exists():  # stop at repo root
            break
    return False


def load_rules() -> list[dict]:
    table = Path(__file__).resolve().parent.parent.parent / "data" / "route-signals.json"
    try:
        doc = json.loads(table.read_text())
    except Exception:
        return []
    rules = doc.get("rules", [])
    return rules if isinstance(rules, list) else []


def score_rule(rule: dict, text: str, low: str, urls: list[str], has_diff: bool) -> tuple[int, list[str]]:
    """Return (score, evidence-categories-that-fired)."""
    score = 0
    fired: list[str] = []

    for pat in rule.get("url", []):
        rx = re.compile(pat, re.IGNORECASE)
        if any(rx.search(u) for u in urls):
            score += SCORE["url"]
            fired.append("url")
            break

    for pat in rule.get("regex", []):
        if re.search(pat, text):
            score += SCORE["regex"]
            fired.append("regex")
            break

    for needle in rule.get("paths", []):
        if needle.lower() in low:
            score += SCORE["path"]
            fired.append("path")
            break

    if rule.get("diff") and has_diff:
        score += SCORE["diff"]
        fired.append("diff")

    for phrase in rule.get("intents", []):
        if phrase.lower() in low:
            score += SCORE["intent"]
            fired.append("intent")
            break

    return score, fired


def why(fired: list[str]) -> str:
    label = {"url": "URL", "regex": "id key", "path": "path", "diff": "inline diff", "intent": "phrasing"}
    seen: list[str] = []
    for f in fired:  # preserve order, dedupe
        if label[f] not in seen:
            seen.append(label[f])
    return " + ".join(seen)


def main() -> int:
    prompt = read_prompt()
    if not prompt or muted():
        return 0

    rules = load_rules()
    if not rules:
        return 0

    low = prompt.lower()
    urls = URL_RE.findall(prompt)
    has_diff = bool(DIFF_RE.search(prompt))

    candidates = []
    for rule in rules:
        score, fired = score_rule(rule, prompt, low, urls, has_diff)
        if score <= 0:
            continue
        if not any(f in HARD_KINDS for f in fired):
            continue  # intent-only never fires
        candidates.append((score, rule, fired))

    if not candidates:
        return 0

    # Highest score first; stable on table order for ties.
    candidates.sort(key=lambda c: -c[0])
    if candidates[0][0] < MIN_SCORE:
        return 0

    top = candidates[:MAX_CANDIDATES]

    print("[polymath-core route] Prompt signals suggest a Polymath surface:")
    for score, rule, fired in top:
        kind = rule.get("kind", "skill")
        print(f"  - {rule['surface']}  ({kind} — {why(fired)})")
    # Surface a named alternative from the top rule if it adds a distinct option.
    alt = top[0][1].get("alt")
    if alt and all(alt != r["surface"] for _, r, _ in top):
        print(f"    alternative: {alt}")
    # Trust: DECLARED metadata only. No executor consumes this yet, so it
    # is surfaced descriptively and must NOT read as permission to skip the
    # propose-first contract (run-workflow SKILL.md still owns "never auto-start").
    # Reconciled 2026-06-08 after review flagged the permissive wording as a
    # contradiction with the executor and with reality (0 surfaces flipped).
    top_trust = top[0][1].get("trust")
    if top_trust == "auto-headless":
        print("    trust: auto-headless (declared) — eligible for non-interactive auto-run once an executor honors the axis; today still propose-first.")
    print("Detect-only; nothing was run. Confirm with /polymath-core:route, or proceed.")
    print("Silence: POLYMATH_ROUTE_MUTE=1 or touch .polymath/route-muted")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Degrade quiet: a hint must never break a turn.
        sys.exit(0)
