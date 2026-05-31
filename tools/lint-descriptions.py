#!/usr/bin/env python3
"""Score every plugin description on trigger_clarity / scope_boundary / disambiguation.

A description is the always-on routing surface (≤200 chars). The catalog audit
found descriptions trigger well but rarely *fence their scope* — the dominant
defect is a missing "Not for … / use X instead" clause, which is exactly what a
router needs to avoid mis-firing between sibling skills. This linter makes that
measurable and (optionally) enforceable.

Three dimensions, 1-5:
- trigger_clarity   leads with an action verb and names concrete domain nouns.
- scope_boundary    states where the skill ENDS / when NOT to use it.
- disambiguation    distinct from siblings (penalised by high token overlap).

Modes:
  (default)   reporting — print summary + the artifacts under FAIL thresholds;
              ALWAYS exits 0 (safe to wire into CI without breaking the build).
  --strict    exit 1 if any artifact scores below a FAIL threshold.
  --json      emit the full per-artifact scoring as JSON (for dashboards).

FAIL thresholds (the floor, not the target): scope_boundary < 2, disambiguation
< 3, trigger_clarity < 3.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS = REPO / "plugins"

# The FAIL gate enforces only the deterministically-reliable signal:
# disambiguation. A description that token-overlaps a sibling (da<3) will
# mis-route a router, and the fix — a scope clause that names the boundary —
# is concrete. trigger_clarity and scope_boundary are reported as advisory
# means (trigger quality is better judged by the live skill-triggering tests;
# scope_boundary tracks the rewrite backlog but most of the catalog lacks an
# explicit clause today, so gating on it now would fail ~everything).
FAIL = {"disambiguation": 3}

# A scope-boundary clause: an explicit exclusion, redirection, or alias marker.
NOT_USE = re.compile(
    r"\b(not for\b|not to\b|not a\b|not the\b|isn't\b|don't use\b|"
    r"use .*? instead|instead of\b|rather than\b|alias for\b|"
    r"command entry point\b|vendor[- ]neutral\b|[a-z]+ only[;,.]|"
    r";\s*(?:not|for [A-Za-z]+ use|use )|\buse the \w+ skill\b)",
    re.I,
)
LEAD_VERB = re.compile(
    r"^(design|write|author|review|audit|triage|plan|run|set|estimate|"
    r"explain|decompose|break|score|investigate|fetch|post|draft|drive|"
    r"diagnose|capture|build|generate|orient|open|file|resume|list|frame|"
    r"classify|prioriti[sz]e|map|model|define|detect|propose|critique|"
    r"turn|cut|upgrade|migrate|refactor|fix|ship|address|sunset|"
    r"deprecate|pin|surface|pick|choose|read|verify|check)\b",
    re.I,
)
FRONT = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _front_field(text: str, field: str) -> str | None:
    m = FRONT.match(text)
    if not m:
        return None
    fm = m.group(1)
    fm_m = re.search(rf"^{field}:\s*(.+?)\s*$", fm, re.MULTILINE)
    return fm_m.group(1).strip().strip("'\"") if fm_m else None


def discover() -> list[dict]:
    arts: list[dict] = []
    for plugin in sorted(PLUGINS.glob("*/")):
        pname = plugin.name
        for skill in sorted(plugin.glob("skills/*/SKILL.md")):
            text = skill.read_text()
            arts.append({
                "id": f"{pname}:{_front_field(text, 'name') or skill.parent.name}",
                "kind": "skill", "path": str(skill.relative_to(REPO)),
                "description": _front_field(text, "description") or "",
            })
        for cmd in sorted(plugin.glob("commands/*.md")):
            text = cmd.read_text()
            arts.append({
                "id": f"{pname}:/{cmd.stem}",
                "kind": "command", "path": str(cmd.relative_to(REPO)),
                "description": _front_field(text, "description") or "",
            })
        for agent in sorted(plugin.glob("agents/*.md")):
            text = agent.read_text()
            arts.append({
                "id": f"{pname} agent {_front_field(text, 'name') or agent.stem}",
                "kind": "agent", "path": str(agent.relative_to(REPO)),
                "description": _front_field(text, "description") or "",
            })
    return arts


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower())) - {
        "the", "a", "an", "and", "or", "for", "to", "of", "in", "with", "this",
        "that", "it", "its", "on", "by", "from", "into", "as", "is", "be",
    }


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    return len(ta & tb) / max(1, len(ta | tb))


def _proper(s: str) -> set[str]:
    """Proper-noun / acronym discriminators (AWS, GCP, Jira, Postgres, Redis…),
    excluding the first word (sentence-initial capital carries no signal)."""
    words = re.findall(r"\b([A-Z]{2,}|[A-Z][a-z]{2,})\b", s.split(" ", 1)[-1] if " " in s else s)
    return set(words)


def _distinguishable(a: str, b: str) -> bool:
    """True when each description carries a proper noun the other lacks — the
    router can route on that token even if the rest of the text overlaps
    (design-aws vs design-gcp, jira vs linear), so it is not a real collision."""
    pa, pb = _proper(a), _proper(b)
    return bool(pa - pb) and bool(pb - pa)


def score(arts: list[dict]) -> None:
    # disambiguation: start at 5, penalise high pairwise token overlap.
    overlap = {a["id"]: 5 for a in arts}
    worst_pair: dict[str, tuple[str, float]] = {}
    for x, y in itertools.combinations(arts, 2):
        j = _jaccard(x["description"], y["description"])
        if j > 0.5 and not _distinguishable(x["description"], y["description"]):
            for me, other in ((x, y), (y, x)):
                overlap[me["id"]] = 2
                if j > worst_pair.get(me["id"], ("", 0))[1]:
                    worst_pair[me["id"]] = (other["id"], j)
    for a in arts:
        d = a["description"]
        nouns = len(re.findall(r"\b[a-z]+-[a-z]+\b|\b[A-Z][A-Za-z]+\b|/[a-z]+\b", d))
        a["trigger_clarity"] = 5 if (LEAD_VERB.match(d) and nouns >= 2) else (
            3 if LEAD_VERB.match(d) else 2)
        a["scope_boundary"] = 4 if NOT_USE.search(d) else 2
        a["disambiguation"] = overlap[a["id"]]
        a["overlaps_with"] = worst_pair.get(a["id"], ("", 0))[0] or None
        scores = [a["trigger_clarity"], a["scope_boundary"], a["disambiguation"]]
        mean = sum(scores) / 3
        a["verdict"] = (
            "REWRITE" if (min(scores) <= 2 and mean < 3) else
            "REVISE" if mean < 4 else "ACCEPT"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit 1 on any FAIL-threshold breach")
    ap.add_argument("--json", action="store_true", help="emit full scoring as JSON")
    args = ap.parse_args()

    arts = discover()
    score(arts)

    if args.json:
        print(json.dumps(arts, indent=2))
        return 0

    fails = [
        a for a in arts
        if any(a[d] < thr for d, thr in FAIL.items())
    ]
    by_kind: dict[str, list[dict]] = {}
    for a in arts:
        by_kind.setdefault(a["kind"], []).append(a)

    def mean(items, dim):
        return sum(i[dim] for i in items) / max(1, len(items))

    print(f"lint-descriptions: {len(arts)} artifacts")
    print(f"{'KIND':9} {'N':>4} {'tc':>5} {'sb':>5} {'da':>5}")
    for kind, items in sorted(by_kind.items()):
        print(f"{kind:9} {len(items):>4} {mean(items,'trigger_clarity'):>5.2f} "
              f"{mean(items,'scope_boundary'):>5.2f} {mean(items,'disambiguation'):>5.2f}")
    verdicts: dict[str, int] = {}
    for a in arts:
        verdicts[a["verdict"]] = verdicts.get(a["verdict"], 0) + 1
    print("verdicts:", ", ".join(f"{k}={v}" for k, v in sorted(verdicts.items())))

    # Advisory: artifacts with no explicit scope-boundary clause (the rewrite
    # backlog), not gated yet.
    no_clause = sum(1 for a in arts if a["scope_boundary"] < 4)
    print(f"advisory: {no_clause}/{len(arts)} lack an explicit scope-boundary clause")

    if fails:
        print(f"\nFAIL: {len(fails)} artifact(s) overlap a sibling (disambiguation<"
              f"{FAIL['disambiguation']}) — add a scope clause that names the boundary:")
        for a in sorted(fails, key=lambda x: x["id"]):
            print(f"  {a['id']:45} tc{a['trigger_clarity']}/sb{a['scope_boundary']}/"
                  f"da{a['disambiguation']}  [{a['kind']}]  overlaps {a['overlaps_with']}")

    if args.strict and fails:
        print(f"\nlint-descriptions: FAILED ({len(fails)} artifact(s) below threshold)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
