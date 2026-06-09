#!/usr/bin/env python3
"""AGENT-1: every plugin agent has a baseline-beating golden fixture, and no
agent collides with a workflow's routing intent.

An agent is the forked-context surface (docs/PLUGIN-AUTHORING.md §6). The
contract there is that a new agent ships with a golden fixture showing the
forked-context agent surfaces something a same-input no-agent baseline misses.
This gate makes that prose enforceable and blocks the role-as-agent
anti-pattern (§6.1) from regressing in silently.

For each plugins/<plugin>/agents/<name>.md:
  - frontmatter declares `name` (== file stem) and `description`;
  - a golden fixture tests/golden/<plugin>/agent-<name>.md exists, whose
    frontmatter sets `agent: <name>` and carries an `expect` block (the trace).
    The `expect.not_invoked` / `disable_tools` fields are how the fixture
    encodes the no-agent baseline contrast.

Collision guard: an agent must not compete with a workflow on intent —
its `name` must not equal any workflow `name`, and neither its name nor its
description may contain a workflow trigger phrase verbatim.

Exit 1 on any problem.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS = REPO / "plugins"
GOLDEN = REPO / "tests" / "golden"
WORKFLOWS = PLUGINS / "polymath-flows" / "workflows"


def frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end + 1]) or {}
    except yaml.YAMLError:
        return {}


def workflow_intents() -> tuple[set[str], set[str]]:
    """Return (workflow names, trigger phrases) across all workflows."""
    names: set[str] = set()
    triggers: set[str] = set()
    for wf in sorted(WORKFLOWS.glob("*.yaml")):
        data = frontmatter(wf) or yaml.safe_load(wf.read_text())
        if not isinstance(data, dict):
            continue
        if data.get("name"):
            names.add(data["name"])
        for t in data.get("triggers", []) or []:
            triggers.add(str(t).strip().lower())
    return names, triggers


def main() -> int:
    problems: list[str] = []
    wf_names, wf_triggers = workflow_intents()

    agents = sorted(PLUGINS.glob("*/agents/*.md"))
    for agent in agents:
        plugin = agent.parents[1].name
        stem = agent.stem
        fm = frontmatter(agent)
        name = fm.get("name")
        desc = (fm.get("description") or "").strip()

        if not name:
            problems.append(f"{plugin}/agents/{stem}.md: frontmatter missing `name`")
            name = stem
        elif name != stem:
            problems.append(f"{plugin}/agents/{stem}.md: frontmatter name {name!r} != file stem {stem!r}")
        if not desc:
            problems.append(f"{plugin}/agents/{stem}.md: frontmatter missing `description`")

        # AGENT-1: a baseline-beating golden fixture must exist.
        fixture = GOLDEN / plugin / f"agent-{stem}.md"
        if not fixture.exists():
            problems.append(
                f"{plugin}/agents/{stem}.md: no golden fixture at "
                f"tests/golden/{plugin}/agent-{stem}.md (AGENT-1 — see PLUGIN-AUTHORING §6)"
            )
        else:
            ffm = frontmatter(fixture)
            if ffm.get("agent") != stem:
                problems.append(f"tests/golden/{plugin}/agent-{stem}.md: frontmatter `agent` must be {stem!r}")
            if "expect" not in ffm:
                problems.append(f"tests/golden/{plugin}/agent-{stem}.md: missing `expect` block (the agent-vs-baseline trace)")

        # Collision guard: agents must not compete with a workflow intent.
        if name in wf_names:
            problems.append(f"{plugin}/agents/{stem}.md: agent name {name!r} collides with a workflow name")
        dl = desc.lower()
        for trig in wf_triggers:
            if trig and (trig == name.lower() or trig in dl):
                problems.append(
                    f"{plugin}/agents/{stem}.md: name/description contains workflow trigger phrase {trig!r} "
                    f"(an agent must not compete with a workflow on intent)"
                )
                break

    if problems:
        for p in problems:
            print(f"  ✗ AGENT-1: {p}", file=sys.stderr)
        print(f"\ncheck-agents: {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print(f"check-agents: {len(agents)} agent(s) — all have baseline-beating fixtures, no workflow-intent collisions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
