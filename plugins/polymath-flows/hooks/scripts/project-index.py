#!/usr/bin/env python3
"""polymath-flows SessionStart injection: catalog index + project fragment.

Renders the catalog workflow index (data/workflow-index.min.json, built by
tools/build-workflow-index.py) and extends it with a machine-local, tiered
fragment indexing workflows the catalog cannot see: the project layer
(./.claude/polymath/workflows/) and the user layer
(${CLAUDE_CONFIG_DIR}/polymath/workflows/, fallback ~/.claude/polymath/
workflows/) — the same directories bin/polymath-flow resolves at `start`.
Without this, project/user workflows are runnable but invisible: the agent
can never propose what it was never told exists.

The fragment is written to <data_root>/polymath-flows/
workflow-index.project.json — machine-local plugin data, never the checked-in
data/ dir (which the WORKFLOW-INDEX conformance gate byte-diffs). Producer and
consumer are both this plugin, so the per-plugin namespacing of
CLAUDE_PLUGIN_DATA never splits them.

Tier and collision rules:
  - project tier wins over user tier on a name collision (runner resolution
    order); a name matching a catalog workflow is kept but annotated as
    shadowing, since `start <name>` would resolve the project file.
  - a trigger phrase colliding with a catalog trigger (from the full
    workflow-index.json) or an earlier-tier entry is DROPPED from the
    fragment and recorded in dropped_triggers — never an error, the catalog
    keeps the phrase. This mirrors WORKFLOW-2's uniqueness rule with the
    asymmetry localization needs (project config must not fail the session).

The catalog block (header / entry lines / footer) is kept byte-identical to
tools/build-workflow-index.py's render_injection() so the builder's
MAX_INJECTION_TOKENS assertion measures exactly what is surfaced. The project
block is additive, appears only when project/user workflows exist, and is
deliberately outside that token assertion. A repo with no project or user
workflows produces byte-identical output to the catalog-only rendering.

Fail-open everywhere: a malformed workflow YAML is skipped, an unwritable
data dir skips the fragment write, any unexpected error still prints the
catalog block. Nothing here may break a session start.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import sys

# Keep byte-identical to tools/build-workflow-index.py (INJECTION_HEADER /
# INJECTION_FOOTER / TIER_A_BUDGET / TIER_B_POINTER / select_tier_a) — the
# builder owns the budget; a unit test pins the two files equal.
INJECTION_HEADER = "Polymath workflows available (multi-step arcs you can run):"
INJECTION_FOOTER = (
    "Before starting substantial multi-step work that matches one of these, first "
    "propose that workflow in one line (name in backticks) and wait for approval; "
    "otherwise just answer. Never start a workflow without asking."
)
TIER_A_BUDGET = 400
TIER_B_POINTER = (
    "  …plus {n} more — full list: polymath-flows data/workflow-index.json; "
    "ask /polymath-core:route to pick."
)
PROJECT_HEADER = "Project workflows (machine-local additions; same propose-first contract):"

# Repo-relevance probing is bounded exactly like polymath-core's
# write-repo-evidence.py: probe count capped, total wall budget 200ms,
# fail-open (an unprobed workflow simply isn't boosted into Tier A).
MAX_RELEVANCE_PROBES = 64
RELEVANCE_BUDGET_SECONDS = 0.200


def estimate_tokens(text: str) -> int:
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


def _repo_root() -> pathlib.Path | None:
    here = pathlib.Path.cwd()
    for d in (here, *here.parents):
        if (d / ".git").exists() or (d / ".polymath").is_dir():
            return d
    return None


def relevant_workflows(detect_records: list[dict]) -> set[str]:
    """Workflow names whose detectionSignals paths match this repo —
    existence probes against the repo root (exact path / 'dir/' / glob,
    one level of ** allowed). Bounded and fail-open."""
    import time

    root = _repo_root()
    if root is None:
        return set()
    relevant: set[str] = set()
    probes = 0
    deadline = time.monotonic() + RELEVANCE_BUDGET_SECONDS
    for rec in detect_records:
        name = rec.get("n")
        if not isinstance(name, str) or not name:
            continue
        for probe in rec.get("paths") or []:
            if not isinstance(probe, str) or not probe:
                continue
            if probes >= MAX_RELEVANCE_PROBES or time.monotonic() > deadline:
                return relevant
            probes += 1
            try:
                if any(ch in probe for ch in "*?["):
                    hit = next(root.glob(probe), None) is not None
                elif probe.endswith("/"):
                    hit = (root / probe.rstrip("/")).is_dir()
                else:
                    hit = (root / probe).exists()
            except Exception:
                continue
            if hit:
                relevant.add(name)
                break  # one hit is enough for this workflow
    return relevant

FRAGMENT_NAME = "workflow-index.project.json"
MAX_FRAGMENT_ENTRIES = 30  # sanity cap; a project layer is a handful of files

# [ \t]* (not \s*) so a null value never captures the NEXT line; list items
# may sit at column 0 — that is what yaml.safe_dump (and `polymath-flow
# flatten`) emits for block sequences.
_NAME_RE = re.compile(r"^name:[ \t]*(.+?)[ \t]*$", re.MULTILINE)
_WHEN_RE = re.compile(r"^whenToUse:[ \t]*(.+?)[ \t]*$", re.MULTILINE)
_TRIGGERS_RE = re.compile(r"^triggers:[ \t]*$((?:\n[ \t]*-[ \t]*.+)+)", re.MULTILINE)
_TRIGGER_ITEM_RE = re.compile(r"^[ \t]*-[ \t]*(.+?)[ \t]*$", re.MULTILINE)
# A captured block-scalar indicator means the real value is multi-line —
# unindexable by the line-scan; treat as missing (fail open).
_BLOCK_INDICATORS = {"|", ">", "|-", ">-", "|+", ">+"}


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _extract_meta(text: str) -> dict:
    """Pull name / whenToUse / triggers out of a workflow YAML. Uses PyYAML
    when importable; otherwise a line-scan good enough for one-line scalars
    (a multi-line whenToUse is simply not indexed — fail open)."""
    try:
        import yaml  # type: ignore

        doc = yaml.safe_load(text)
        if isinstance(doc, dict):
            return {
                "name": doc.get("name"),
                "whenToUse": doc.get("whenToUse"),
                "triggers": [t for t in (doc.get("triggers") or []) if isinstance(t, str)],
            }
        return {}
    except Exception:
        pass
    meta: dict = {"name": None, "whenToUse": None, "triggers": []}
    m = _NAME_RE.search(text)
    if m:
        meta["name"] = _unquote(m.group(1))
    m = _WHEN_RE.search(text)
    if m:
        meta["whenToUse"] = _unquote(m.group(1))
    m = _TRIGGERS_RE.search(text)
    if m:
        meta["triggers"] = [_unquote(t) for t in _TRIGGER_ITEM_RE.findall(m.group(1))]
    return meta


def _normalize_when(when: object) -> str | None:
    """Reduce a whenToUse value to an injectable one-liner, or None.
    A multi-line value would smear the injection across lines; a captured
    block-scalar indicator (no-PyYAML path) means the real text is
    multi-line too."""
    if not isinstance(when, str):
        return None
    when = when.strip()
    if not when or "\n" in when or when in _BLOCK_INDICATORS:
        return None
    return when


def _tier_dirs() -> list[tuple[str, pathlib.Path]]:
    """Mirror bin/polymath-flow's _resolve_workflow layers exactly: project,
    then ${CLAUDE_CONFIG_DIR} user dir, then the ~/.claude user fallback
    (the runner checks BOTH user locations, so both are indexed)."""
    tiers: list[tuple[str, pathlib.Path]] = [
        ("project", pathlib.Path.cwd() / ".claude" / "polymath" / "workflows"),
    ]
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        tiers.append(("user", pathlib.Path(config_dir) / "polymath" / "workflows"))
    fallback = pathlib.Path.home() / ".claude" / "polymath" / "workflows"
    if not any(d == fallback for _, d in tiers):
        tiers.append(("user", fallback))
    return tiers


def collect_fragment(catalog_names: set[str], catalog_triggers: dict[str, str]) -> dict:
    entries: list[dict] = []
    dropped: list[dict] = []
    seen_names: set[str] = set()
    seen_triggers: dict[str, str] = dict(catalog_triggers)
    for tier, directory in _tier_dirs():
        try:
            paths = sorted(directory.glob("*.yaml"))
        except OSError:
            continue
        for path in paths:
            if len(entries) >= MAX_FRAGMENT_ENTRIES:
                break
            try:
                meta = _extract_meta(path.read_text(errors="ignore"))
            except OSError:
                continue
            declared = meta.get("name")
            when = _normalize_when(meta.get("whenToUse"))
            if not isinstance(declared, str) or not declared or not when:
                continue  # not indexable; still runnable by explicit name
            # `polymath-flow start <name>` resolves by FILE STEM, so the
            # stem is the only honest proposable handle; the YAML `name:`
            # is recorded when it diverges (doctor visibility).
            name = path.stem
            if name in seen_names:
                continue  # narrower tier already owns this name
            seen_names.add(name)
            kept: list[str] = []
            for trigger in meta.get("triggers") or []:
                owner = seen_triggers.get(trigger)
                if owner is not None:
                    dropped.append(
                        {"n": name, "trigger": trigger, "collides_with": owner}
                    )
                    continue
                seen_triggers[trigger] = name
                kept.append(trigger)
            entry = {"n": name, "w": when, "tier": tier, "path": str(path), "t": kept}
            if declared != name:
                entry["declaredName"] = declared
            if name in catalog_names:
                entry["shadows"] = True
            entries.append(entry)
    return {
        "version": 1,
        "root": str(pathlib.Path.cwd()),
        "built_at": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "entries": entries,
        "dropped_triggers": dropped,
    }


def render(min_records: list[dict], fragment: dict, relevant: set[str] | None = None) -> str:
    relevant = relevant or set()
    lines: list[str] = []
    if min_records:
        tier_a, tier_b = select_tier_a(min_records, relevant)
        lines.append(INJECTION_HEADER)
        lines += [f"  - {r['n']}: {r['w']}" for r in tier_a]
        if tier_b:
            lines.append(TIER_B_POINTER.format(n=len(tier_b)))
        lines.append(INJECTION_FOOTER)
    entries = fragment.get("entries") or []
    if entries:
        lines.append(PROJECT_HEADER)
        for e in entries:
            suffix = ""
            if e.get("tier") == "user":
                suffix += " [user layer]"
            if e.get("shadows"):
                suffix += " [overrides the catalog workflow of this name]"
            lines.append(f"  - {e['n']}: {e['w']}{suffix}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        return 0
    min_index_path = pathlib.Path(argv[1])
    full_index_path = pathlib.Path(argv[2])
    data_root = pathlib.Path(argv[3])
    detect_index_path = pathlib.Path(argv[4]) if len(argv) > 4 else None

    min_records: list[dict] = []
    try:
        loaded = json.loads(min_index_path.read_text())
        if isinstance(loaded, list):
            min_records = [r for r in loaded if isinstance(r, dict) and "n" in r and "w" in r]
    except Exception:
        min_records = []

    catalog_names: set[str] = {r["n"] for r in min_records}
    catalog_triggers: dict[str, str] = {}
    try:
        full = json.loads(full_index_path.read_text())
        if isinstance(full, list):
            for r in full:
                if not isinstance(r, dict):
                    continue
                catalog_names.add(r.get("n", ""))
                for t in r.get("t") or []:
                    catalog_triggers.setdefault(t, r.get("n", ""))
    except Exception:
        pass
    catalog_names.discard("")

    relevant: set[str] = set()
    if detect_index_path is not None:
        try:
            detect = json.loads(detect_index_path.read_text())
            if isinstance(detect, list):
                relevant = relevant_workflows([r for r in detect if isinstance(r, dict)])
        except Exception:
            relevant = set()

    try:
        fragment = collect_fragment(catalog_names, catalog_triggers)
    except Exception:
        fragment = {"entries": []}

    # Doctor-visible tiering record: which workflows made Tier A, how many
    # collapsed to the pointer, and which RELEVANT ones did not fit (the
    # overflow that should prompt a whenToUse trim or a budget discussion).
    try:
        tier_a, tier_b = select_tier_a(min_records, relevant)
        tier_a_names = [r["n"] for r in tier_a]
        fragment["tiering"] = {
            "tier_a": tier_a_names,
            "tier_b_count": len(tier_b),
            "relevant": sorted(relevant),
            "overflow_relevant": sorted(
                n for n in relevant if n not in set(tier_a_names)
            ),
            "budget_tokens": TIER_A_BUDGET,
        }
    except Exception:
        pass

    try:
        target_dir = data_root / "polymath-flows"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / FRAGMENT_NAME).write_text(
            json.dumps(fragment, indent=2, ensure_ascii=False) + "\n"
        )
    except Exception:
        pass  # unwritable data dir must not cost the injection

    text = render(min_records, fragment, relevant)
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:
        sys.exit(0)  # a session start must never break on indexing
