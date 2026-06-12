#!/usr/bin/env python3
"""polymath-core SessionStart repo-evidence writer.

Evaluates the repo-state probes declared by routing sidecars (`repo_state:`,
compiled into the `repo_probes` list of data/route-signals.json — plus any
declared by the project overlay .polymath/route-signals.project.json) against
the current repo root, and caches the booleans in
``${CLAUDE_PLUGIN_DATA}/polymath-core/repo-evidence.json``.

route-hint.py reads that cache at prompt time and gives a rule a +1 soft
boost when one of its declared probes is true — repo context (a Dockerfile,
*.tf files, a k8s/ dir) sharpening prompt-time scoring without per-prompt
filesystem walks.

Bounded by construction, fail-open by contract:
* probe count is capped (MAX_PROBES = 64; the builder enforces the same cap
  at compile time)
* total wall budget is 200ms — when exceeded, remaining probes are simply
  not recorded (absent != false: route-hint treats missing keys as no boost)
* any error -> exit 0, nothing written or a stale file left in place; a
  SessionStart hook must never break a session.

Probe semantics against the repo root:
  'name/'   -> directory exists
  '*glob*'  -> any glob match (one level of ** allowed; first hit wins)
  'name'    -> path exists (file or dir)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

MAX_PROBES = 64
BUDGET_SECONDS = 0.200


def repo_root(start: Path) -> Path | None:
    here = start.resolve()
    for d in (here, *here.parents):
        if (d / ".git").exists() or (d / ".polymath").is_dir():
            return d
    return None


def data_path() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        root = Path(base)
        # Layouts vary: some harnesses point CLAUDE_PLUGIN_DATA at the
        # per-plugin dir, some at the shared parent. Write under
        # polymath-core/ unless we're already inside it.
        if root.name != "polymath-core":
            root = root / "polymath-core"
        return root / "repo-evidence.json"
    return Path.home() / ".claude" / "plugins" / "data" / "polymath-core" / "repo-evidence.json"


def load_probes(root: Path) -> list[str]:
    probes: list[str] = []
    table = Path(__file__).resolve().parent.parent.parent / "data" / "route-signals.json"
    try:
        doc = json.loads(table.read_text())
        for p in doc.get("repo_probes") or []:
            if isinstance(p, str) and p:
                probes.append(p)
    except Exception:
        pass
    overlay = root / ".polymath" / "route-signals.project.json"
    try:
        doc = json.loads(overlay.read_text())
        for rule in doc.get("rules") or []:
            if isinstance(rule, dict):
                for p in rule.get("repo_state") or []:
                    if isinstance(p, str) and p and p not in probes:
                        probes.append(p)
    except Exception:
        pass
    return probes[:MAX_PROBES]


def evaluate(root: Path, probes: list[str]) -> dict[str, bool]:
    evidence: dict[str, bool] = {}
    deadline = time.monotonic() + BUDGET_SECONDS
    for probe in probes:
        if time.monotonic() > deadline:
            break  # absent != false: unrecorded probes simply give no boost
        try:
            if any(ch in probe for ch in "*?["):
                evidence[probe] = next(root.glob(probe), None) is not None
            elif probe.endswith("/"):
                evidence[probe] = (root / probe.rstrip("/")).is_dir()
            else:
                evidence[probe] = (root / probe).exists()
        except Exception:
            continue
    return evidence


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    cwd = payload.get("cwd") if isinstance(payload, dict) else None
    root = repo_root(Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd())
    if root is None:
        return 0
    probes = load_probes(root)
    if not probes:
        return 0
    evidence = evaluate(root, probes)
    out = data_path()
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"root": str(root), "evidence": evidence}, indent=2))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
