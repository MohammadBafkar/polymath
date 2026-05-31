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

The rendered min-index (the text the hook actually injects) is asserted to stay
under MAX_INJECTION_TOKENS; over budget exits 1 and names the longest whenToUse.
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

# Injection framing — kept byte-identical to the SessionStart hook so the
# token assertion measures what is actually surfaced.
INJECTION_HEADER = "Polymath workflows available (propose before running):"
INJECTION_FOOTER = "When a request matches one, name it and ask before running it."
# Ceiling on the always-on routing surface. The full catalog is one consolidated
# block of ~18 tokens per workflow (name + terse whenToUse) plus framing. 450
# fits the current 22 workflows with headroom; if the catalog grows past ~30,
# replace the flat list with a collapsed/tiered surface rather than raising this.
MAX_INJECTION_TOKENS = 450


def _count_tokens(text: str) -> int:
    try:
        import tiktoken  # type: ignore

        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        # Heuristic fallback (chars / 4) — matches token-budget.sh's posture.
        return len(text) // 4 + 1


def render_injection(min_records: list[dict]) -> str:
    lines = [INJECTION_HEADER]
    lines += [f"  - {r['n']}: {r['w']}" for r in min_records]
    lines.append(INJECTION_FOOTER)
    return "\n".join(lines)


def collect() -> tuple[list[dict], list[dict], list[dict], list[str]]:
    full, mini, detect = [], [], []
    warnings: list[str] = []
    seen_triggers: dict[str, str] = {}
    no_routing: list[str] = []

    for path in sorted(WORKFLOWS_DIR.glob("*.yaml")):
        wf = yaml.safe_load(path.read_text()) or {}
        name = wf.get("name")
        when = wf.get("whenToUse")
        triggers = wf.get("triggers") or []
        signals = wf.get("detectionSignals") or {}
        if not name:
            warnings.append(f"{path.name}: missing name; skipped")
            continue
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
                warnings.append(
                    f"duplicate trigger {t!r} in {name} and {seen_triggers[t]}"
                )
            seen_triggers[t] = name

    if no_routing:
        warnings.append(
            "no whenToUse/triggers (not indexed): " + ", ".join(sorted(no_routing))
        )

    full.sort(key=lambda r: r["n"])
    mini.sort(key=lambda r: r["n"])
    detect.sort(key=lambda r: r["n"])
    return full, mini, detect, warnings


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
    args = ap.parse_args()

    full, mini, detect, warnings = collect()
    for w in warnings:
        print(f"build-workflow-index: warning: {w}", file=sys.stderr)

    # Token budget on the rendered injection (what the hook surfaces).
    rendered = render_injection(mini)
    tokens = _count_tokens(rendered)
    if tokens > MAX_INJECTION_TOKENS:
        longest = max(mini, key=lambda r: len(r["w"]))
        print(
            f"build-workflow-index: rendered min-index is ~{tokens} tokens "
            f"(>{MAX_INJECTION_TOKENS}). Trim the longest whenToUse: "
            f"{longest['n']} ({len(longest['w'])} chars).",
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
        print(f"workflow-index OK ({len(mini)} workflows, ~{tokens} injection tokens)")
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for fname, content in files.items():
        (DATA_DIR / fname).write_text(content)
    print(
        f"wrote {len(files)} index files for {len(mini)} workflows "
        f"(~{tokens} injection tokens) to {DATA_DIR.relative_to(REPO)}/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
