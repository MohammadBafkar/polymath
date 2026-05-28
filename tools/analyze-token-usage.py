#!/usr/bin/env python3
"""Token-usage analyzer.

Parses a `claude -p --output-format stream-json` transcript and breaks
down token consumption by:

  - main conversation (the lead model)
  - per-subagent (Agent tool invocations)
  - per-skill (Skill tool invocations and the skill text loaded)
  - per-tool category (Read, Bash, Edit, Write, Grep, …)

Every time you propose adding an agent, run the analyzer against a
representative transcript to confirm the agent saves tokens (or earns
them through quality the no-agent baseline can't match). The
"no-agent baseline" comparison is the falsifiability anchor.

Usage:

    tools/analyze-token-usage.py <transcript.jsonl>
    tools/analyze-token-usage.py --baseline <baseline.jsonl> --candidate <candidate.jsonl>

When run with --baseline/--candidate, prints a side-by-side delta plus a
recommendation (PROCEED / REJECT / INCONCLUSIVE).

Field tolerance:
  Transcripts vary by Claude Code version. The analyzer treats every
  field as optional and reports gracefully when usage data is absent
  (e.g. transcripts saved before stream-json gained `usage` blocks).
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Bucket:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    events: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cache_total(self) -> int:
        return self.cache_read_tokens + self.cache_creation_tokens

    def add_usage(self, usage: dict[str, Any]) -> None:
        self.input_tokens += int(usage.get("input_tokens") or 0)
        self.output_tokens += int(usage.get("output_tokens") or 0)
        self.cache_read_tokens += int(usage.get("cache_read_input_tokens") or 0)
        self.cache_creation_tokens += int(usage.get("cache_creation_input_tokens") or 0)
        self.events += 1


@dataclass
class Report:
    main: Bucket = field(default_factory=Bucket)
    subagents: dict[str, Bucket] = field(default_factory=lambda: collections.defaultdict(Bucket))
    skills: dict[str, Bucket] = field(default_factory=lambda: collections.defaultdict(Bucket))
    tools: dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))

    @property
    def total_tokens(self) -> int:
        total = self.main.total
        total += sum(b.total for b in self.subagents.values())
        return total


def _iter_events(path: pathlib.Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _content_of(message: Any) -> list[Any]:
    if isinstance(message, dict):
        c = message.get("content")
        if isinstance(c, list):
            return c
    return []


def analyze(events: list[dict[str, Any]]) -> Report:
    r = Report()
    active_subagent: str | None = None

    for ev in events:
        # The shape used by stream-json today nests message under `message`.
        msg = ev.get("message")
        usage = None
        if isinstance(msg, dict):
            usage = msg.get("usage") if isinstance(msg.get("usage"), dict) else None
        if usage is None and isinstance(ev.get("usage"), dict):
            usage = ev["usage"]

        bucket = r.subagents[active_subagent] if active_subagent else r.main
        if usage:
            bucket.add_usage(usage)

        for node in _content_of(msg) + ([ev] if isinstance(ev, dict) else []):
            if not isinstance(node, dict):
                continue
            if node.get("type") == "tool_use":
                name = node.get("name") or "?"
                r.tools[name] = r.tools.get(name, 0) + 1
                inp = node.get("input") if isinstance(node.get("input"), dict) else {}
                if name == "Agent":
                    sub = inp.get("subagent_type") or inp.get("description") or "subagent"
                    active_subagent = str(sub)
                if name == "Skill":
                    sk = inp.get("skill") or "?"
                    r.skills.setdefault(str(sk), Bucket()).events += 1
            if node.get("type") == "tool_result":
                # Heuristic: subagent ends when its tool_result lands.
                # If a parent message follows without an Agent invocation in
                # between, we treat the subagent context as closed.
                tu_id = node.get("tool_use_id")
                if tu_id and active_subagent:
                    # We don't track the matching Agent tool_use_id; assume
                    # any tool_result that's a "result" type closes the
                    # active subagent. Good enough for the aggregate view.
                    active_subagent = None
    return r


def _fmt_bucket(b: Bucket) -> str:
    return (
        f"in={b.input_tokens:>8}  out={b.output_tokens:>7}  "
        f"cache_r={b.cache_read_tokens:>8}  cache_w={b.cache_creation_tokens:>7}  "
        f"events={b.events:>4}"
    )


def render(r: Report, *, label: str = "") -> str:
    lines: list[str] = []
    if label:
        lines.append(f"# {label}")
    lines.append("## Main conversation")
    lines.append(_fmt_bucket(r.main))
    if r.subagents:
        lines.append("\n## Subagents")
        for name in sorted(r.subagents, key=lambda k: -r.subagents[k].total):
            lines.append(f"  {name:30}  {_fmt_bucket(r.subagents[name])}")
    if r.skills:
        lines.append("\n## Skills invoked")
        for name in sorted(r.skills, key=lambda k: -r.skills[k].events):
            lines.append(f"  {name:40}  events={r.skills[name].events}")
    if r.tools:
        lines.append("\n## Tools used")
        for name in sorted(r.tools, key=lambda k: -r.tools[k]):
            lines.append(f"  {name:30}  {r.tools[name]:>4}")
    lines.append("")
    lines.append(f"TOTAL tokens (main+subagents): {r.total_tokens}")
    return "\n".join(lines)


def compare(baseline: Report, candidate: Report) -> str:
    delta = candidate.total_tokens - baseline.total_tokens
    pct = (
        (delta / baseline.total_tokens) * 100
        if baseline.total_tokens
        else float("inf") if delta else 0.0
    )
    verdict = "INCONCLUSIVE"
    if delta < 0 and abs(pct) >= 5:
        verdict = "PROCEED (candidate uses fewer tokens)"
    elif delta > 0 and pct >= 20:
        verdict = "REJECT (candidate uses materially more tokens — quality must justify)"
    elif abs(pct) < 5:
        verdict = "INCONCLUSIVE (within noise; decide on quality, not tokens)"

    out: list[str] = []
    out.append("# Baseline")
    out.append(render(baseline))
    out.append("\n# Candidate")
    out.append(render(candidate))
    out.append("")
    out.append("# Delta")
    out.append(
        f"baseline_total = {baseline.total_tokens}, "
        f"candidate_total = {candidate.total_tokens}, "
        f"delta = {delta:+d} tokens ({pct:+.1f}%)"
    )
    out.append(f"verdict: {verdict}")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript", nargs="?")
    parser.add_argument("--baseline")
    parser.add_argument("--candidate")
    args = parser.parse_args()

    if args.baseline and args.candidate:
        base = analyze(_iter_events(pathlib.Path(args.baseline)))
        cand = analyze(_iter_events(pathlib.Path(args.candidate)))
        print(compare(base, cand))
        return 0
    if not args.transcript:
        parser.error("either <transcript> or --baseline + --candidate is required")
    r = analyze(_iter_events(pathlib.Path(args.transcript)))
    print(render(r, label=args.transcript))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
