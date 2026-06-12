#!/usr/bin/env python3
"""polymath-core UserPromptSubmit ambient routing hint.

Reads the user's prompt from a Claude Code hook payload on stdin, extracts
*deterministic* signals (URLs, ticket/CVE keys, file paths mentioned in the
prompt, inline diffs, intent phrasings), scores them against the bundled
``data/route-signals.json`` table, and — only when a HARD signal is present —
prints one quiet line proposing the smallest Polymath surface that fits.

Design contract:

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
SCORE = {"url": 3, "regex": 3, "path": 2, "diff": 2, "intent": 1, "repo": 1}
MIN_SCORE = 3          # best candidate must clear this to emit
MAX_CANDIDATES = 3     # never show the user more than a 1-of-3 choice

DIFF_RE = re.compile(r"(?m)^(?:diff --git |@@ .*@@|\+\+\+ |--- |index [0-9a-f]{7,})")
URL_RE = re.compile(r"https?://[^\s)>\]\"']+")


def repo_root() -> Path | None:
    here = Path.cwd()
    for d in (here, *here.parents):
        if (d / ".git").exists() or (d / ".polymath").is_dir():
            return d
    return None


def load_evidence() -> dict:
    """Repo-state booleans cached by write-repo-evidence.py at SessionStart.
    Only honored when the cache was written for THIS repo root — stale
    evidence from another repo must never boost anything (and that root
    guard is also what keeps hermetic fixture runs inert)."""
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        root = Path(base)
        if root.name != "polymath-core":
            root = root / "polymath-core"
        cache = root / "repo-evidence.json"
    else:
        cache = Path.home() / ".claude" / "plugins" / "data" / "polymath-core" / "repo-evidence.json"
    try:
        doc = json.loads(cache.read_text())
    except Exception:
        return {}
    here = repo_root()
    if here is None or doc.get("root") != str(here):
        return {}
    evidence = doc.get("evidence")
    return evidence if isinstance(evidence, dict) else {}


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


# Project overlays are intentionally small: the table is scanned per prompt,
# and a project should add a handful of company-specific signals, not a
# second catalog.
MAX_PROJECT_RULES = 50


def load_project_rules() -> list[dict]:
    """Project routing overlay: `.polymath/route-signals.project.json`,
    found by walking cwd up to the repo root (same walk as the mute marker).
    Same `rules` shape as the bundled table. Lenient by design — a rule
    missing `surface` or carrying no signal is skipped, a malformed file is
    ignored entirely; project config must never break a turn. The SURFACE-2
    uniqueness gate stays marketplace-internal: an overlay may duplicate a
    catalog intent, and scoring (with project rules sorted first on ties)
    resolves it at runtime."""
    here = Path.cwd()
    path = None
    for d in (here, *here.parents):
        cand = d / ".polymath" / "route-signals.project.json"
        if cand.exists():
            path = cand
            break
        if (d / ".git").exists():  # stop at repo root
            break
    if path is None:
        return []
    try:
        doc = json.loads(path.read_text())
    except Exception:
        return []
    rules = doc.get("rules", []) if isinstance(doc, dict) else []
    if not isinstance(rules, list):
        return []
    out: list[dict] = []
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get("surface"), str):
            continue
        sane = _sanitize_project_rule(rule)
        if sane is None:
            continue
        out.append(sane)
        if len(out) >= MAX_PROJECT_RULES:
            break
    return out


def _sanitize_project_rule(rule: dict) -> dict | None:
    """Normalise one overlay rule to exactly what score_rule expects.
    Signal fields must be lists of strings (a bare string would iterate
    per-character and false-fire on nearly every prompt); url/regex
    patterns must compile (one bad pattern must not take down the whole
    hook); `trust` is stripped — a project file can never claim an
    elevated trust axis. Returns None when nothing scoreable survives."""
    sane: dict = {"surface": rule["surface"], "_project": True}
    if isinstance(rule.get("kind"), str):
        sane["kind"] = rule["kind"]
    if isinstance(rule.get("alt"), str):
        sane["alt"] = rule["alt"]
    for key in ("url", "regex"):
        patterns = rule.get(key)
        if not isinstance(patterns, list):
            continue
        kept = []
        for pat in patterns:
            if not isinstance(pat, str):
                continue
            try:
                re.compile(pat)
            except re.error:
                continue
            kept.append(pat)
        if kept:
            sane[key] = kept
    for key in ("paths", "intents", "not_intents", "repo_state"):
        values = rule.get(key)
        if isinstance(values, list):
            kept = [v for v in values if isinstance(v, str) and v]
            if kept:
                sane[key] = kept
    if rule.get("diff") is True:
        sane["diff"] = True
    if not any(sane.get(k) for k in ("url", "regex", "paths", "diff", "intents")):
        return None
    return sane


def score_rule(
    rule: dict, text: str, low: str, urls: list[str], has_diff: bool, evidence: dict
) -> tuple[int, list[str]]:
    """Return (score, evidence-categories-that-fired)."""
    # Veto first: a matching not_intent removes the surface from scoring
    # entirely, regardless of what its positive signals would say.
    for phrase in rule.get("not_intents", []):
        if phrase.lower() in low:
            return 0, []

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

    # Repo-state boost (soft): cached evidence sharpens scoring but can
    # never satisfy the hard-signal firing requirement.
    for probe in rule.get("repo_state", []):
        if evidence.get(probe):
            score += SCORE["repo"]
            fired.append("repo")
            break

    return score, fired


def why(fired: list[str]) -> str:
    label = {"url": "URL", "regex": "id key", "path": "path", "diff": "inline diff", "intent": "phrasing", "repo": "repo state"}
    seen: list[str] = []
    for f in fired:  # preserve order, dedupe
        if label[f] not in seen:
            seen.append(label[f])
    return " + ".join(seen)


def main() -> int:
    prompt = read_prompt()
    if not prompt or muted():
        return 0

    # Project overlay rules come FIRST: the sort below is stable on table
    # order, so at equal score the project's localization wins the tie.
    rules = load_project_rules() + load_rules()
    if not rules:
        return 0

    low = prompt.lower()
    urls = URL_RE.findall(prompt)
    has_diff = bool(DIFF_RE.search(prompt))
    evidence = load_evidence()

    candidates = []
    for rule in rules:
        score, fired = score_rule(rule, prompt, low, urls, has_diff, evidence)
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
        if rule.get("_project"):
            kind = f"{kind}, project overlay"
        print(f"  - {rule['surface']}  ({kind} — {why(fired)})")
    # Surface a named alternative from the top rule if it adds a distinct option.
    alt = top[0][1].get("alt")
    if alt and all(alt != r["surface"] for _, r, _ in top):
        print(f"    alternative: {alt}")
    # Trust: in hint mode (this hook) the declaration is surfaced
    # descriptively and must NOT read as permission to skip the
    # propose-first contract (run-workflow SKILL.md still owns "never
    # auto-start"). polymath-pipeline honors auto-headless for read-only
    # surfaces when the project declares routing.mode classify|enforce.
    top_trust = top[0][1].get("trust")
    if top_trust == "auto-headless":
        print("    trust: auto-headless (declared) — honored for read-only use by polymath-pipeline when routing.mode != hint; in hint mode still propose-first.")
    print("Detect-only; nothing was run. Confirm with /polymath-core:route, or proceed.")
    print("Silence: POLYMATH_ROUTE_MUTE=1 or touch .polymath/route-muted")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Degrade quiet: a hint must never break a turn.
        sys.exit(0)
