#!/usr/bin/env python3
"""Compile per-surface routing declarations into the deterministic route table.

This is the SINGLE PRODUCER of ``plugins/polymath-core/data/route-signals.json``
— the table the ``polymath-core`` route-hint hook scores prompts against. That
file used to be hand-maintained and carried a ``_note`` admitting it had to be
"kept loosely in sync" with the workflow detect table; this builder removes the
hand-sync by deriving the table from declarations that live next to each surface.

A *surface* (skill, workflow, or — from Phase 3 — tool) declares its own
deterministic routing in a sidecar YAML the builder globs but no other tool
touches:

  skills/tools  ->  plugins/<plugin>/skills/<skill>/routing.yaml
  workflows     ->  plugins/polymath-flows/routing/<workflowName>.yaml

``kind`` / ``id`` / the proposed ``surface`` string are DERIVED from the file
location, so a declaration cannot drift from the surface it routes to. Each
sidecar's body validates against ``registry/schemas/surface-routing.schema.json``.

Two outputs under plugins/polymath-core/data/:
  route-signals.json   the scored table consumed by route-hint.py
  surface-index.json   catalog of routable surfaces (capabilities / trust / alt)

Modes:
  (default)   build and write both files; warn on duplicate intents.
  --check     build in memory and diff against disk; exit 1 on drift.
  --strict    SURFACE-2: every intent / url / regex pattern must be unique
              across all surfaces; exit 1 on collision.

This builder runs ALONGSIDE build-workflow-index.py: that one produces the
always-on SessionStart workflow index (Dispatch Layer 2) from workflow
whenToUse/triggers; this one produces the deterministic prompt-time table
from routeSignals.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - CI always has PyYAML
    print("build-surface-index: PyYAML is required", file=sys.stderr)
    sys.exit(2)

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS = REPO / "plugins"
DATA_DIR = REPO / "plugins" / "polymath-core" / "data"
WORKFLOW_ROUTING = PLUGINS / "polymath-flows" / "routing"
SCHEMA_PATH = REPO / "registry" / "schemas" / "surface-routing.schema.json"
TOOL_SCHEMA_PATH = REPO / "registry" / "schemas" / "tool.schema.json"

KIND_RANK = {"workflow": 0, "skill": 1, "tool": 2, "agent": 3}
# Canonical key order for each emitted rule (route-hint.py is order-agnostic;
# this only keeps the generated file stable so --check is a real diff-guard).
RULE_KEY_ORDER = (
    "id", "kind", "surface", "alt", "url", "regex", "paths", "diff",
    "intents", "not_intents", "repo_state", "tier", "trust", "capabilities",
)
# Hard cap on the union of declared repo_state probes — the SessionStart
# evidence writer must stay constant-time (≤64 probes, 200ms budget).
MAX_REPO_PROBES = 64

# HINT-BUDGET: ceiling on the worst SINGLE-CANDIDATE ambient hint render —
# header + the table's costliest candidate line (every declared signal kind
# firing) + its alternative line + the trust line + the footer. The
# 3-candidate ceiling is this budget plus two more candidate lines; the
# install-affordance suffix (not-installed path) is deliberately outside.
# Mirrors route-hint.py's templates — keep in sync (the gate measures real
# rule data, so template bloat or a verbose new surface fails here).
HINT_BUDGET_TOKENS = 120
HINT_HEADER = "[polymath-core route] Prompt signals suggest a Polymath surface:"
HINT_TRUST_LINE = (
    "    trust: auto-headless — read-only may run unconfirmed in "
    "classify/enforce mode; otherwise propose-first."
)
HINT_FOOTER = (
    "Detect-only; nothing ran. Confirm: /polymath-core:route. "
    "Mute: POLYMATH_ROUTE_MUTE=1 or .polymath/route-muted"
)
HINT_WHY_LABELS = {
    "url": "URL", "regex": "id key", "paths": "path", "diff": "inline diff",
    "intents": "phrasing", "repo_state": "repo state",
}


def _estimate_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def hint_budget_report(rules: list[dict]) -> tuple[int, str, list[str]]:
    """(worst_tokens, worst_surface, render_lines) for the costliest
    single-candidate hint this table can produce."""
    worst_tokens, worst_surface, worst_lines = 0, "", []
    for rule in rules:
        why = " + ".join(
            HINT_WHY_LABELS[k] for k in ("url", "regex", "paths", "diff", "intents", "repo_state")
            if rule.get(k)
        )
        kind = rule.get("kind", "skill")
        lines = [HINT_HEADER, f"  - {rule['surface']}  ({kind} — {why})"]
        if rule.get("alt"):
            lines.append(f"    alternative: {rule['alt']}")
        if rule.get("trust") == "auto-headless":
            lines.append(HINT_TRUST_LINE)
        lines.append(HINT_FOOTER)
        tokens = _estimate_tokens("\n".join(lines))
        if tokens > worst_tokens:
            worst_tokens, worst_surface, worst_lines = tokens, rule["surface"], lines
    return worst_tokens, worst_surface, worst_lines


def hint_budget_self_test() -> int:
    """Prove HINT-BUDGET can fail: a synthetic rule with a bloated surface
    name and every signal kind must exceed the budget."""
    bloated = {
        "surface": "polymath-overweight:" + "x" * 400,
        "kind": "workflow",
        "url": ["u"], "regex": ["r"], "paths": ["p"], "diff": True,
        "intents": ["i"], "repo_state": ["s"], "alt": "polymath-x:y",
        "trust": "auto-headless",
    }
    tokens, _, _ = hint_budget_report([bloated])
    if tokens <= HINT_BUDGET_TOKENS:
        print("hint-budget --self-test FAILED: synthetic bloated rule passed", file=sys.stderr)
        return 1
    print(f"hint-budget --self-test: synthetic bloated rule correctly over budget (~{tokens} tokens)")
    return 0

GENERATED_NOTE_SIGNALS = (
    "GENERATED by tools/build-surface-index.py from per-surface routing.yaml "
    "sidecars. Do not edit by hand; edit the surface's routing.yaml and rerun "
    "the builder (the SURFACE-INDEX conformance gate fails on drift)."
)
GENERATED_NOTE_INDEX = (
    "GENERATED by tools/build-surface-index.py. Catalog of routable Polymath "
    "surfaces and their capabilities/trust. Do not edit by hand."
)


def _load_schema() -> dict | None:
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except Exception:
        return None


def _validate(body: dict, schema: dict | None, where: str, errors: list[str]) -> None:
    if schema is None:
        return
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(body, schema)
    except ImportError:
        # Minimal manual fallback: reject unknown keys + require a hard signal.
        allowed = set(schema.get("properties", {}))
        unknown = set(body) - allowed
        if unknown:
            errors.append(f"{where}: unknown key(s) {sorted(unknown)}")
        if not any(k in body for k in ("url", "regex", "paths", "diff", "events")):
            errors.append(f"{where}: needs at least one signal (url/regex/paths/diff/events)")
        if "schemaVersion" in body and body["schemaVersion"] != 1:
            errors.append(f"{where}: schemaVersion must be 1")
        if "tier" in body and body["tier"] not in ("hard", "soft"):
            errors.append(f"{where}: tier must be hard|soft")
    except Exception as e:  # jsonschema.ValidationError
        msg = getattr(e, "message", str(e))
        errors.append(f"{where}: {msg}")
    _validate_semantics(body, where, errors)


def _validate_semantics(body: dict, where: str, errors: list[str]) -> None:
    """Checks the JSON schema cannot express: event regexes must compile,
    a surface must not veto its own intents."""
    import re

    for i, ev in enumerate(body.get("events") or []):
        if not isinstance(ev, dict):
            continue
        for key in ("command", "output"):
            pat = ev.get(key)
            if isinstance(pat, str):
                try:
                    re.compile(pat)
                except re.error as e:
                    errors.append(f"{where}: events[{i}].{key} regex does not compile ({e})")
    own = {s.lower() for s in body.get("intents") or []}
    veto = {s.lower() for s in body.get("not_intents") or []}
    clash = own & veto
    if clash:
        errors.append(f"{where}: not_intents veto this surface's own intents {sorted(clash)}")


def _validate_tool_manifest(path: pathlib.Path, errors: list[str]) -> None:
    """TOOL-1: a tools/<name>/tool.json must validate against tool.schema.json."""
    where = str(path.relative_to(REPO))
    try:
        body = json.loads(path.read_text())
    except Exception as e:
        errors.append(f"{where}: invalid JSON ({e})")
        return
    if body.get("name") and body["name"] != path.parent.name:
        errors.append(f"{where}: tool name {body['name']!r} != directory {path.parent.name!r}")
    try:
        tool_schema = json.loads(TOOL_SCHEMA_PATH.read_text())
    except Exception:
        return
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(body, tool_schema)
    except ImportError:
        for k in ("name", "summary"):
            if k not in body:
                errors.append(f"{where}: missing required key {k!r}")
    except Exception as e:
        errors.append(f"{where}: {getattr(e, 'message', str(e))}")


def _declaration(path: pathlib.Path, kind: str, ident: str, surface: str, errors: list[str]) -> dict | None:
    where = str(path.relative_to(REPO))
    try:
        body = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:  # malformed sidecar -> clean error, not a traceback
        errors.append(f"{where}: invalid YAML ({e})")
        return None
    return {"kind": kind, "id": ident, "surface": surface, "body": body, "where": where}


def collect() -> tuple[list[dict], list[str]]:
    """Return (declarations, errors). Each declaration: kind/id/surface/body."""
    decls: list[dict] = []
    errors: list[str] = []
    schema = _load_schema()

    # Skills (and Phase-3 tools share this sidecar shape).
    for sidecar in sorted(PLUGINS.glob("*/skills/*/routing.yaml")):
        rel = sidecar.relative_to(PLUGINS).parts  # (plugin, 'skills', skill, 'routing.yaml')
        plugin, skill = rel[0], rel[2]
        d = _declaration(sidecar, "skill", skill, f"{plugin}:{skill}", errors)
        if d is None:
            continue
        _validate(d["body"], schema, d["where"], errors)
        decls.append(d)

    # Workflows — routing sidecars live OUTSIDE workflows/ so the *.yaml
    # workflow glob and `polymath-flow validate` never see them.
    if WORKFLOW_ROUTING.is_dir():
        for sidecar in sorted(WORKFLOW_ROUTING.glob("*.yaml")):
            name = sidecar.stem
            d = _declaration(sidecar, "workflow", name, f"polymath-flows:run-workflow {name}", errors)
            if d is None:
                continue
            _validate(d["body"], schema, d["where"], errors)
            decls.append(d)

    # Agents — forked-context critics/scouts. The sidecar sits beside the
    # agent's .md (agents/<name>.routing.yaml; agents are files, not dirs);
    # the agent definition must exist so a declaration cannot outlive its
    # surface.
    for sidecar in sorted(PLUGINS.glob("*/agents/*.routing.yaml")):
        rel = sidecar.relative_to(PLUGINS).parts  # (plugin, 'agents', '<name>.routing.yaml')
        plugin = rel[0]
        name = sidecar.name[: -len(".routing.yaml")]
        if not (sidecar.parent / f"{name}.md").is_file():
            errors.append(
                f"{str(sidecar.relative_to(REPO))}: no agent definition {name}.md beside it"
            )
        d = _declaration(sidecar, "agent", name, f"{plugin}:{name}", errors)
        if d is None:
            continue
        _validate(d["body"], schema, d["where"], errors)
        decls.append(d)

    # Tools (Phase 3) — first-class routable units. Every tools/<name>/ must carry
    # a tool.json manifest (TOOL-1); a routing.yaml beside it makes the tool a
    # deterministically-routed surface, identical in shape to a skill sidecar.
    for manifest in sorted(PLUGINS.glob("*/tools/*/tool.json")):
        _validate_tool_manifest(manifest, errors)
    for sidecar in sorted(PLUGINS.glob("*/tools/*/routing.yaml")):
        rel = sidecar.relative_to(PLUGINS).parts  # (plugin, 'tools', tool, 'routing.yaml')
        plugin, tool = rel[0], rel[2]
        if not (sidecar.parent / "tool.json").exists():
            errors.append(f"{str(sidecar.relative_to(REPO))}: routable tool missing tool.json (TOOL-1)")
        d = _declaration(sidecar, "tool", tool, f"{plugin}:{tool}", errors)
        if d is None:
            continue
        _validate(d["body"], schema, d["where"], errors)
        decls.append(d)

    # The `trust` axis is now constrained by the surface-routing schema enum
    # ({propose, auto-headless}) — `_validate` above rejects an unconditional
    # `auto`. This replaced the bespoke TRUST-1 gate that used to live here.

    decls.sort(key=lambda d: (KIND_RANK.get(d["kind"], 9), d["id"]))
    return decls, errors


def check_uniqueness(decls: list[dict]) -> list[str]:
    """Every intent / url / regex pattern must belong to at most one surface."""
    problems: list[str] = []
    for field in ("intents", "url", "regex"):
        seen: dict[str, str] = {}
        for d in decls:
            for val in d["body"].get(field, []) or []:
                if val in seen and seen[val] != d["surface"]:
                    problems.append(f"{field} {val!r} claimed by both {seen[val]} and {d['surface']}")
                seen[val] = d["surface"]
    return problems


def build_rule(d: dict) -> dict:
    body = d["body"]
    rule: dict = {"id": d["id"], "kind": d["kind"], "surface": d["surface"]}
    if body.get("alt"):
        rule["alt"] = body["alt"]
    for k in ("url", "regex", "paths"):
        if body.get(k):
            rule[k] = list(body[k])
    if body.get("diff"):
        rule["diff"] = True
    for k in ("intents", "not_intents", "repo_state"):
        if body.get(k):
            rule[k] = list(body[k])
    # Carry tier only when it deviates from the default ('soft'); the
    # surface-index carries it for every surface (the ratchet's view).
    if body.get("tier") == "hard":
        rule["tier"] = "hard"
    # Carry trust only when it differs from the default (keeps the table lean);
    # route-hint.py surfaces it so the agent knows a surface is auto-eligible.
    if body.get("trust") and body["trust"] != "propose":
        rule["trust"] = body["trust"]
    # Re-key into canonical order.
    return {k: rule[k] for k in RULE_KEY_ORDER if k in rule}


def build_index_entry(d: dict) -> dict:
    body = d["body"]
    entry: dict = {"surface": d["surface"], "kind": d["kind"]}
    if body.get("alt"):
        entry["alt"] = body["alt"]
    if body.get("capabilities"):
        entry["capabilities"] = list(body["capabilities"])
    entry["trust"] = body.get("trust", "propose")
    entry["tier"] = body.get("tier", "soft")
    if body.get("chainsTo"):
        entry["chainsTo"] = list(body["chainsTo"])
    return entry


def build_events(decls: list[dict]) -> list[dict]:
    """Flatten every declaration's `events` into the compiled event table
    consumed by event-trigger.py (PostToolUse)."""
    events: list[dict] = []
    for d in decls:
        for ev in d["body"].get("events") or []:
            entry = {
                "id": d["id"],
                "surface": d["surface"],
                "command": ev["command"],
                "output": ev["output"],
                "why": ev["why"],
            }
            if ev.get("note"):
                entry["note"] = ev["note"]
            events.append(entry)
    return events


def collect_repo_probes(decls: list[dict]) -> tuple[list[str], list[str]]:
    """(sorted probe union, errors). The union across the catalog is capped
    at MAX_REPO_PROBES so the SessionStart evidence writer stays bounded."""
    probes: set[str] = set()
    for d in decls:
        probes.update(d["body"].get("repo_state") or [])
    errors: list[str] = []
    if len(probes) > MAX_REPO_PROBES:
        errors.append(
            f"declared repo_state probes union is {len(probes)} — exceeds the "
            f"{MAX_REPO_PROBES}-probe cap (the SessionStart evidence writer is bounded)"
        )
    return sorted(probes), errors


def serialize(decls: list[dict]) -> dict[str, str]:
    rules = [build_rule(d) for d in decls]
    probes, _ = collect_repo_probes(decls)
    signals: dict = {"version": 1, "_generated": GENERATED_NOTE_SIGNALS, "rules": rules}
    events = build_events(decls)
    if events:
        signals["events"] = events
    if probes:
        signals["repo_probes"] = probes
    index = {
        "_generated": GENERATED_NOTE_INDEX,
        "counts": {
            "routable": len(decls),
            "workflows": sum(1 for d in decls if d["kind"] == "workflow"),
            "skills": sum(1 for d in decls if d["kind"] == "skill"),
            "tools": sum(1 for d in decls if d["kind"] == "tool"),
            "agents": sum(1 for d in decls if d["kind"] == "agent"),
        },
        "surfaces": [build_index_entry(d) for d in decls],
    }
    return {
        "route-signals.json": json.dumps(signals, indent=2, ensure_ascii=False) + "\n",
        "surface-index.json": json.dumps(index, indent=2, ensure_ascii=False) + "\n",
    }


def _coverage_note(decls: list[dict]) -> str:
    total_skills = sum(1 for _ in PLUGINS.glob("*/skills/*/SKILL.md"))
    routable_skills = sum(1 for d in decls if d["kind"] == "skill")
    total_wf = sum(1 for _ in (PLUGINS / "polymath-flows" / "workflows").glob("*.yaml"))
    routable_wf = sum(1 for d in decls if d["kind"] == "workflow")
    tools = sum(1 for d in decls if d["kind"] == "tool")
    return (
        f"deterministic dispatch covers {routable_skills}/{total_skills} skills, "
        f"{routable_wf}/{total_wf} workflows, {tools} tools"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile per-surface routing into route-signals.json + surface-index.json")
    ap.add_argument("--check", action="store_true", help="verify on-disk files match a fresh build; exit 1 on drift")
    ap.add_argument("--strict", action="store_true", help="SURFACE-2: intents/url/regex must be globally unique; exit 1 on collision")
    ap.add_argument("--hint-budget", action="store_true", help="HINT-BUDGET: worst single-candidate hint render must stay ≤ %d tokens" % HINT_BUDGET_TOKENS)
    ap.add_argument("--self-test", action="store_true", help="with --hint-budget: prove the budget gate can fail")
    args = ap.parse_args()

    if args.hint_budget and args.self_test:
        return hint_budget_self_test()

    decls, errors = collect()
    errors += collect_repo_probes(decls)[1]
    if errors:
        for e in errors:
            print(f"build-surface-index: invalid declaration: {e}", file=sys.stderr)
        return 1

    if args.hint_budget:
        rules = [build_rule(d) for d in decls]
        tokens, surface, lines = hint_budget_report(rules)
        if tokens > HINT_BUDGET_TOKENS:
            print(
                f"build-surface-index: HINT-BUDGET: worst single-candidate hint is "
                f"~{tokens} tokens (>{HINT_BUDGET_TOKENS}), driven by {surface} — "
                f"trim the surface name/alt or the hint template",
                file=sys.stderr,
            )
            for line in lines:
                print(f"    {line}", file=sys.stderr)
            return 1
        print(f"hint-budget OK (worst single-candidate ~{tokens} tokens ≤ {HINT_BUDGET_TOKENS}; driver: {surface})")
        return 0

    dupes = check_uniqueness(decls)
    if dupes:
        if args.strict:
            for d in dupes:
                print(f"build-surface-index: SURFACE-2: {d}", file=sys.stderr)
            return 1
        for d in dupes:
            print(f"build-surface-index: warning: duplicate {d}", file=sys.stderr)

    files = serialize(decls)

    if args.check:
        drift = [f for f, content in files.items() if not (DATA_DIR / f).exists() or (DATA_DIR / f).read_text(encoding="utf-8") != content]
        if drift:
            print("build-surface-index: stale (run tools/build-surface-index.py): " + ", ".join(drift), file=sys.stderr)
            return 1
        print(f"surface-index OK ({len(decls)} routable surfaces) — {_coverage_note(decls)}")
        return 0

    if args.strict:
        # Enforcement-only mode: SURFACE-2 checks already passed above; never write
        # (so `--strict` can't silently mutate a dirty tree; `--check` is the guard).
        print(f"surface-index OK (strict; {len(decls)} routable surfaces)")
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for fname, content in files.items():
        (DATA_DIR / fname).write_text(content, encoding="utf-8")
    print(f"wrote route-signals.json + surface-index.json ({len(decls)} routable surfaces) to {DATA_DIR.relative_to(REPO)}/")
    print(f"  {_coverage_note(decls)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
