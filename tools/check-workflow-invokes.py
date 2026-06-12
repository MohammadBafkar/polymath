#!/usr/bin/env python3
"""Assert every workflow step's `invoke: plugin:skill` resolves to a real skill.

Workflows hard-code `invoke:` routing labels (docs/PLUGIN-AUTHORING.md § 5.1).
If a skill is renamed or removed, a workflow can silently point at nothing —
no existing gate catches it. This guard resolves every `invoke:` target to
`plugins/<plugin>/skills/<skill>/SKILL.md`.

Capability-resolved invokes (e.g. `${capabilities.issue_tracker.plugin}:...`)
are skipped — the provider is resolved at run time from
`.polymath/capabilities.yaml`.

It additionally WARNS (does not fail) when a step prompt is long enough to look
like it re-teaches the skill's procedure rather than passing inputs/artifacts —
treat SKILL.md as the single source of procedure.

Usage:
  tools/check-workflow-invokes.py            # check all workflows; exit 1 on unresolved
  tools/check-workflow-invokes.py <file>...  # check named workflow yaml files
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"
PROMPT_RETEACH_CHARS = 700  # advisory only

_INVOKE = re.compile(r"^\s*invoke:\s*(.+?)\s*$", re.MULTILINE)
_PLUGIN_SKILL = re.compile(r"^([a-z0-9-]+):([a-z0-9-]+)$")
_AGENT_LABEL = re.compile(r"^agent:([a-z0-9-]+):([a-z0-9-]+)$")
_DESCRIPTION = re.compile(r"^\s*description:\s*(.+?)\s*$", re.MULTILINE)
DESC_MAX = 200  # workflow.schema.json maxLength on description (workflow + inputs)


def _skill_exists(plugin: str, skill: str) -> bool:
    return (PLUGINS_DIR / plugin / "skills" / skill / "SKILL.md").exists()


def _agent_exists(plugin: str, name: str) -> bool:
    return (PLUGINS_DIR / plugin / "agents" / f"{name}.md").exists()


def check_workflow(path: pathlib.Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    text = path.read_text()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        rel = path.relative_to(REPO)
    except ValueError:
        rel = path  # explicit file argument outside the repo tree

    # Mirror the schema's maxLength:200 on every description (workflow + inputs)
    # so local tooling catches what CI's strict jsonschema would reject.
    for dm in _DESCRIPTION.finditer(text):
        desc = dm.group(1).strip().strip("'\"")
        if len(desc) > DESC_MAX:
            errors.append(f"{rel}: a description is {len(desc)} chars > {DESC_MAX} (workflow.schema.json maxLength)")

    for m in _INVOKE.finditer(text):
        raw = m.group(1).strip().strip("'\"")
        if "${" in raw:
            continue  # capability-resolved at runtime
        ag = _AGENT_LABEL.match(raw)
        if ag:
            plugin, name = ag.group(1), ag.group(2)
            if not _agent_exists(plugin, name):
                errors.append(
                    f"{rel}: invoke `{raw}` resolves to no agent "
                    f"(plugins/{plugin}/agents/{name}.md)"
                )
            continue
        ps = _PLUGIN_SKILL.match(raw)
        if not ps:
            errors.append(
                f"{rel}: invoke `{raw}` is not a plugin:skill or "
                f"agent:plugin:name reference"
            )
            continue
        plugin, skill = ps.group(1), ps.group(2)
        if not _skill_exists(plugin, skill):
            errors.append(f"{rel}: invoke `{plugin}:{skill}` resolves to no SKILL.md")

    # Advisory: flag oversized step prompts (likely re-teaching procedure).
    for pm in re.finditer(r"^\s*prompt:\s*[|>]?\s*\n((?:\s{4,}.*\n?)+)", text):
        block = pm.group(1)
        if len(block) > PROMPT_RETEACH_CHARS:
            warnings.append(
                f"{rel}: a step prompt is {len(block)} chars — confirm it passes "
                f"inputs/artifacts and does not re-teach the skill's procedure"
            )
    return errors, warnings


def main() -> int:
    args = sys.argv[1:]
    if args:
        files = [pathlib.Path(a) if pathlib.Path(a).is_absolute() else REPO / a for a in args]
    else:
        files = sorted(PLUGINS_DIR.glob("*/workflows/*.yaml"))

    total_errors: list[str] = []
    total_warnings: list[str] = []
    for f in files:
        if not f.exists():
            print(f"::warning::not found: {f}", file=sys.stderr)
            continue
        errs, warns = check_workflow(f)
        total_errors.extend(errs)
        total_warnings.extend(warns)

    for w in total_warnings:
        print(f"::warning::{w}")

    if total_errors:
        for e in total_errors:
            print(f"::error::{e}")
        print(f"\nWORKFLOW-INVOKE: {len(total_errors)} unresolved invoke target(s) "
              f"across {len(files)} workflow(s)", file=sys.stderr)
        return 1

    print(f"WORKFLOW-INVOKE: all invoke targets across {len(files)} workflow(s) resolve to a skill")
    return 0


if __name__ == "__main__":
    sys.exit(main())
