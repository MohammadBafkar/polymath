#!/usr/bin/env python3
"""Assert every plugin's README mentions every shipped first-class surface.

For each plugin, enumerate:
  - skills/<slug>/SKILL.md
  - commands/<slug>.md
  - agents/<slug>.md
  - bin/<exe>

Then assert each slug / filename appears in README.md verbatim (the
README may add narrative around it — we only check presence). This
catches the pattern where a README's "What it ships" section lags the
directory after a new skill / command is added.

What we *don't* check (deliberately):
  - `.mcp.json` — README narrative usually says "MCP server: X" and
    that's the substance; the filename is implementation detail.
  - `hooks/hooks.json` — README typically lists hooks by event name
    (`PreToolUse(Write|Edit) — secret-scan`) which is what matters.
  - `workflows/*.yaml` — polymath-flows alone ships 15; listing all
    in every README is overkill.
  - `templates/*` — README narrative or the skill that owns the
    template usually links it.

Usage:
  tools/check-readme-inventory.py               # check all plugins
  tools/check-readme-inventory.py <plugin>...   # check named plugins
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"


def enumerate_surfaces(plugin: pathlib.Path) -> dict[str, list[str]]:
    """Return {surface_type: [name1, name2, ...]} for the plugin."""
    surfaces: dict[str, list[str]] = {}

    skills_dir = plugin / "skills"
    if skills_dir.is_dir():
        surfaces["skills"] = sorted(
            d.name for d in skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        )

    commands_dir = plugin / "commands"
    if commands_dir.is_dir():
        surfaces["commands"] = sorted(
            p.stem for p in commands_dir.glob("*.md")
        )

    agents_dir = plugin / "agents"
    if agents_dir.is_dir():
        surfaces["agents"] = sorted(p.stem for p in agents_dir.glob("*.md"))

    bin_dir = plugin / "bin"
    if bin_dir.is_dir():
        surfaces["bin"] = sorted(p.name for p in bin_dir.iterdir() if p.is_file())

    return surfaces


_CODE_SPAN = re.compile(r"`[^`]+`")


def _mentioned_in_code_or_link(item: str, text: str) -> bool:
    """True if `item` (bare slug) appears as a word inside any backtick
    code span, OR inside a markdown link target / anchor."""
    word = re.compile(rf"\b{re.escape(item)}\b")
    for span in _CODE_SPAN.finditer(text):
        if word.search(span.group(0)):
            return True
    # Markdown links: ](target) and [label](anything-with-item)
    for m in re.finditer(r"\]\(([^)]+)\)", text):
        if word.search(m.group(1)):
            return True
    return False


def check_plugin(plugin: pathlib.Path) -> list[str]:
    """Return a list of error messages; empty list if README is in sync."""
    name = plugin.name
    readme = plugin / "README.md"
    if not readme.exists():
        return [f"{name}: README.md missing"]
    text = readme.read_text()

    surfaces = enumerate_surfaces(plugin)
    errors: list[str] = []
    for kind, items in surfaces.items():
        for item in items:
            # Strip the file extension on bin/ items so `polymath-flow`
            # in bin/ matches a README mention of `polymath-flow`.
            slug = item
            if kind == "bin":
                slug = pathlib.Path(item).stem
            if not _mentioned_in_code_or_link(slug, text):
                errors.append(f"{name}: README does not mention {kind} `{item}`")
    return errors


def main() -> int:
    args = sys.argv[1:]
    if args:
        plugins = [PLUGINS_DIR / a if not a.startswith("plugins/") else REPO / a for a in args]
    else:
        plugins = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())

    total_errors: list[str] = []
    for plugin in plugins:
        if not plugin.is_dir():
            print(f"::warning::not a directory: {plugin}", file=sys.stderr)
            continue
        errs = check_plugin(plugin)
        if errs:
            total_errors.extend(errs)

    if total_errors:
        for e in total_errors:
            print(f"::error::{e}")
        print(f"\nDOCS-2: {len(total_errors)} README inventory drift(s) across {len(plugins)} plugin(s)", file=sys.stderr)
        return 1

    print(f"DOCS-2: all {len(plugins)} plugin READMEs mention every shipped surface")
    return 0


if __name__ == "__main__":
    sys.exit(main())
