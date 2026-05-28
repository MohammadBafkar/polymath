#!/usr/bin/env python3
"""Export every Polymath skill to the agentskills.io v1.0 layout.

agentskills.io v1.0 (https://agentskills.io) is the open standard that
Claude Code, Codex CLI, Cursor, GitHub Copilot, VS Code, Gemini CLI,
Goose, OpenCode, Roo Code, JetBrains Junie, and ~25 other clients read.
Each client looks for SKILL.md files in one or more well-known
directories — `.agents/skills/`, `.codex/skills/`, `.cursor/skills/`,
`.claude/skills/`, `.github/skills/`. They all accept the same
SKILL.md shape: YAML frontmatter (`name` + `description`) + body.

This script materializes Polymath's 124 skills into a portable bundle
under `dist/agents-skills/`. Drop the contents into any of the
well-known directories in your project and the host harness will pick
them up.

What ports:
  - skills/<slug>/SKILL.md → dist/agents-skills/<plugin>-<slug>/SKILL.md
    (frontmatter `name` rewritten to `<plugin>-<slug>` to avoid
    collisions; one such collision exists today —
    file-bug-from-incident is shipped by both polymath-connector-jira
    and polymath-connector-linear).
  - The skill's plugin templates/ directory, IF the SKILL.md body
    references it via `../../templates/`. The references are
    rewritten to `templates/` (relative to the exported skill).
  - dist/agents-skills/manifest.json — maps namespaced names back
    to `<source-plugin>:<source-skill>`.

What does NOT port (Claude-Code-only surfaces):
  - commands/, agents/, hooks/, .mcp.json, workflows/, bin/,
    artifact JSON schemas, .polymath/ project localization.
  See docs/PORTABILITY.md for the full deferral statement.

Usage:
  tools/export-agents-skills.py [--out dist/agents-skills]

The output directory is not committed (covered by dist/ in
.gitignore once added).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"
DEFAULT_OUT = REPO / "dist" / "agents-skills"

FM_NAME = re.compile(r"^name:\s*([^\n]+)$", re.MULTILINE)
TEMPLATE_LINK = re.compile(r"\((\.\./\.\./templates/[^)]+)\)")


def parse_frontmatter(text: str) -> tuple[str, str, str]:
    """Return (frontmatter_text, body, trailing_newline) split out of SKILL.md."""
    if not text.startswith("---"):
        return "", text, ""
    end = text.find("\n---", 3)
    if end == -1:
        return "", text, ""
    fm = text[3:end + 1]
    rest = text[end + 4:]
    if rest.startswith("\n"):
        rest = rest[1:]
    return fm, rest, "\n" if text.endswith("\n") else ""


def export_skill(skill_dir: pathlib.Path, plugin: pathlib.Path, out_root: pathlib.Path) -> dict:
    """Export one skill; return a manifest entry."""
    plugin_name = plugin.name
    skill_name = skill_dir.name
    namespaced = f"{plugin_name}-{skill_name}"
    dest = out_root / namespaced
    dest.mkdir(parents=True, exist_ok=True)

    src_skill = skill_dir / "SKILL.md"
    text = src_skill.read_text()
    fm, body, trailing = parse_frontmatter(text)

    # Rewrite the frontmatter `name` to the namespaced form.
    new_fm, n = FM_NAME.subn(f"name: {namespaced}", fm, count=1)
    if n == 0:
        # No name field; prepend one.
        new_fm = f"name: {namespaced}\n" + fm

    # Rewrite template links from `../../templates/X.md` to `templates/X.md`
    # and remember which templates the skill actually references.
    referenced_templates: set[str] = set()
    def _sub(m: re.Match) -> str:
        target = m.group(1).replace("../../templates/", "templates/")
        referenced_templates.add(m.group(1).split("/")[-1])
        return f"({target})"
    new_body = TEMPLATE_LINK.sub(_sub, body)

    (dest / "SKILL.md").write_text(f"---{new_fm}---\n{new_body}{trailing}")

    # Copy referenced templates (if any).
    src_templates = plugin / "templates"
    copied: list[str] = []
    if referenced_templates and src_templates.is_dir():
        dest_templates = dest / "templates"
        dest_templates.mkdir(exist_ok=True)
        for name in referenced_templates:
            src = src_templates / name
            if src.exists():
                shutil.copy2(src, dest_templates / name)
                copied.append(name)

    # Copy skill-local references/ and scripts/ if present.
    for sub in ("references", "scripts"):
        src_sub = skill_dir / sub
        if src_sub.is_dir():
            shutil.copytree(src_sub, dest / sub, dirs_exist_ok=True)

    return {
        "exported_name": namespaced,
        "source_plugin": plugin_name,
        "source_skill": skill_name,
        "source_path": str(src_skill.relative_to(REPO)),
        "templates_copied": copied,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT,
                        help="Output directory (default: dist/agents-skills)")
    parser.add_argument("--clean", action="store_true",
                        help="Remove the output directory before exporting.")
    args = parser.parse_args()

    out_root: pathlib.Path = args.out
    if args.clean and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for plugin in sorted(PLUGINS_DIR.iterdir()):
        if not plugin.is_dir():
            continue
        skills_dir = plugin / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
                continue
            entry = export_skill(skill_dir, plugin, out_root)
            entries.append(entry)

    manifest = {
        "spec": "agentskills.io",
        "specVersion": "1.0",
        "marketplace": "polymath",
        "skillCount": len(entries),
        "skills": entries,
        "notExported": {
            "rationale": "These surfaces are Claude-Code-specific and do not port via the SKILL.md standard. See docs/PORTABILITY.md.",
            "surfaces": [
                "commands/<slug>.md",
                "agents/<slug>.md",
                "hooks/hooks.json",
                ".mcp.json",
                "workflows/*.yaml (polymath-flows runner)",
                "bin/<exe>",
                "shared/schemas/artifacts/*.json",
                ".polymath/project.yaml + capabilities.yaml",
            ],
        },
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"export-agents-skills: wrote {len(entries)} skill(s) to {out_root.relative_to(REPO)}")
    print(f"manifest:              {(out_root / 'manifest.json').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
