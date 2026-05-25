#!/usr/bin/env python3
"""Validate Polymath agent files and their evidence records."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - CI installs PyYAML
    yaml = None


ROOT = pathlib.Path(__file__).resolve().parents[1]


def frontmatter(path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        raise ValueError("missing YAML frontmatter")
    if yaml is None:
        raise ValueError("PyYAML is required to parse frontmatter")
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def error(path: pathlib.Path, message: str) -> None:
    rel = path.relative_to(ROOT)
    print(f"error: {rel}: {message}", file=sys.stderr)


def validate_agent(plugin_dir: pathlib.Path, agent: pathlib.Path) -> int:
    plugin = plugin_dir.name
    fail = 0
    try:
        fm = frontmatter(agent)
    except ValueError as exc:
        error(agent, str(exc))
        return 1

    name = fm.get("name")
    desc = fm.get("description")
    if name != agent.stem:
        error(agent, f"name must match filename stem {agent.stem!r}")
        fail = 1
    if not isinstance(desc, str) or not desc.strip():
        error(agent, "description is required")
        fail = 1
    elif len(desc) > 200:
        error(agent, f"description is {len(desc)} chars (> 200)")
        fail = 1

    forbidden = {"permissionMode", "hooks", "mcpServers"}
    present = sorted(forbidden & set(fm))
    if present:
        error(agent, f"forbidden plugin-shipped subagent fields: {', '.join(present)}")
        fail = 1

    evidence = ROOT / "tests" / "agent-evidence" / plugin / f"{agent.stem}.md"
    if not evidence.exists():
        error(agent, f"missing evidence file {evidence.relative_to(ROOT)}")
        return 1

    try:
        ev = frontmatter(evidence)
    except ValueError as exc:
        error(evidence, str(exc))
        return 1

    if ev.get("plugin") != plugin:
        error(evidence, f"plugin must be {plugin!r}")
        fail = 1
    if ev.get("agent") != agent.stem:
        error(evidence, f"agent must be {agent.stem!r}")
        fail = 1
    for key in ("scenario", "baseline_prompt", "decision_relevance"):
        if not isinstance(ev.get(key), str) or not ev[key].strip():
            error(evidence, f"{key} is required")
            fail = 1
    for key in ("baseline_misses", "agent_expected_findings"):
        value = ev.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
            error(evidence, f"{key} must be a non-empty string list")
            fail = 1

    fixture_dir = ROOT / "tests" / "golden" / plugin
    fixture_matches = list(fixture_dir.glob(f"*{agent.stem}*.md"))
    if not fixture_matches:
        error(agent, f"missing golden fixture matching tests/golden/{plugin}/*{agent.stem}*.md")
        fail = 1

    return fail


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", help="Validate only one plugin name")
    args = parser.parse_args()

    fail = 0
    plugins = [p for p in (ROOT / "plugins").iterdir() if p.is_dir()]
    for plugin_dir in sorted(plugins):
        if args.plugin and plugin_dir.name != args.plugin:
            continue
        agents_dir = plugin_dir / "agents"
        if not agents_dir.exists():
            continue
        for agent in sorted(agents_dir.glob("*.md")):
            fail |= validate_agent(plugin_dir, agent)

    if fail:
        return 1
    print("agent-evidence: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
