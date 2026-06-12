#!/usr/bin/env python3
"""Fail when a skill-alias command's description merely restates its skill's.

Per the promotion policy (docs/PLUGIN-AUTHORING.md § 5.1), a command's
`description` is counted against the plugin's 400-token always-on budget by
tools/token-report.py budget. A command therefore earns its description only by
saying something the skill description does NOT — *when to reach for the slash
command* — not by paraphrasing the procedure.

This guard targets only **skill-alias commands**: commands whose body says
`Invoke `plugin:skill`` or `alias for `plugin:skill``. Script/guidance commands
(the author scaffolders, plugin-budget) have no target skill and are skipped.

Overlap is the Jaccard similarity of the two descriptions' content-word sets
(lowercased, stopwords + the plugin/skill/command name tokens removed). A
command fails when overlap >= the threshold (default 0.70; override with
POLYMATH_CMD_OVERLAP_MAX).

Usage:
  tools/check-command-overlap.py            # check all; exit 1 on any failure
  tools/check-command-overlap.py --report   # print every overlap, never fail
  tools/check-command-overlap.py <plugin>   # check named plugin(s)
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"
THRESHOLD = float(os.environ.get("POLYMATH_CMD_OVERLAP_MAX", "0.70"))

# Small, deliberately generic stoplist — we want to compare the *substance*
# of the two descriptions, not connective tissue.
STOPWORDS = {
    "a", "an", "and", "or", "the", "for", "of", "to", "in", "on", "with",
    "from", "into", "per", "via", "as", "at", "by", "is", "are", "be", "this",
    "that", "it", "its", "using", "use", "run", "draft", "skill", "command",
    "alias", "thin", "polymath",
}

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_DESC = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
# `Invoke `p:s`` or `alias for [the] `p:s`` anywhere in the body.
_TARGET = re.compile(
    r"(?:Invoke|alias for)[^\n`]*`([a-z0-9-]+):([a-z0-9-]+)`",
    re.IGNORECASE,
)


def _frontmatter(text: str) -> str:
    m = _FRONTMATTER.match(text)
    return m.group(1) if m else ""


def _description(text: str) -> str:
    m = _DESC.search(_frontmatter(text))
    return m.group(1).strip() if m else ""


def _stem(w: str) -> str:
    """Naive singularization so 'plans'/'plan' and 'docs'/'doc' compare equal."""
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("es") and not w.endswith("ses"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def _content_words(desc: str, extra_drop: set[str]) -> set[str]:
    words = re.findall(r"[a-z0-9]+", desc.lower())
    return {
        _stem(w) for w in words
        if w not in STOPWORDS and w not in extra_drop and len(w) > 2
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check_plugin(plugin: pathlib.Path, report: bool) -> tuple[list[str], list[str]]:
    """Return (errors, report_lines)."""
    errors: list[str] = []
    lines: list[str] = []
    commands_dir = plugin / "commands"
    if not commands_dir.is_dir():
        return errors, lines

    for cmd in sorted(commands_dir.glob("*.md")):
        text = cmd.read_text()
        cmd_desc = _description(text)
        if not cmd_desc:
            continue
        m = _TARGET.search(text)
        if not m:
            continue  # not a skill-alias command — nothing to compare
        tgt_plugin, tgt_skill = m.group(1), m.group(2)
        skill_file = PLUGINS_DIR / tgt_plugin / "skills" / tgt_skill / "SKILL.md"
        if not skill_file.exists():
            errors.append(
                f"{plugin.name}: command `{cmd.stem}` aliases "
                f"`{tgt_plugin}:{tgt_skill}` which has no SKILL.md"
            )
            continue
        skill_desc = _description(skill_file.read_text())
        drop = {tgt_plugin, tgt_skill, cmd.stem, *tgt_plugin.split("-"),
                *tgt_skill.split("-"), *cmd.stem.split("-")}
        overlap = _jaccard(_content_words(cmd_desc, drop), _content_words(skill_desc, drop))
        flag = "FAIL" if overlap >= THRESHOLD else "ok"
        lines.append(f"  {overlap:0.2f} {flag:4} {plugin.name}:{cmd.stem} → {tgt_plugin}:{tgt_skill}")
        if overlap >= THRESHOLD and not report:
            errors.append(
                f"{plugin.name}: command `{cmd.stem}` description overlaps its target "
                f"skill `{tgt_plugin}:{tgt_skill}` at {overlap:0.2f} >= {THRESHOLD:0.2f}. "
                f"Make it a complementary 'when to type the slash command' phrase, not a restatement."
            )
    return errors, lines


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--report"]
    report = "--report" in sys.argv[1:]
    if args:
        plugins = [PLUGINS_DIR / a if not a.startswith("plugins/") else REPO / a for a in args]
    else:
        plugins = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())

    total_errors: list[str] = []
    all_lines: list[str] = []
    for plugin in plugins:
        if not plugin.is_dir():
            continue
        errs, lines = check_plugin(plugin, report)
        total_errors.extend(errs)
        all_lines.extend(lines)

    if report:
        print("overlap report (threshold "
              f"{THRESHOLD:0.2f}; skill-alias commands only):")
        for line in sorted(all_lines, reverse=True):
            print(line)
        return 0

    if total_errors:
        for e in total_errors:
            print(f"::error::{e}")
        print(f"\nCOMMAND-OVERLAP: {len(total_errors)} duplicate command description(s)", file=sys.stderr)
        return 1

    print("COMMAND-OVERLAP: all skill-alias command descriptions are complementary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
