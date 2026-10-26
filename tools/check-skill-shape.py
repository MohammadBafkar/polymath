#!/usr/bin/env python3
"""check-skill-shape — the SKILL.md structure contract (SKILL-2/3/4).

The style guide (plugins/polymath-author/references/skill-style-guide.md)
fixes the shape every SKILL.md follows; this makes it a gate instead of a
convention.

  SKILL-2  sections   `## When to use`, `## Inputs`, `## Procedure`, `## Output`,
                      and a `## Quality bar` or `## Anti-patterns…` section.
  SKILL-3  mode       exactly one `**Mode:**` line, carrying the canonical
                      sentence for one of: deterministic, analytical, generative.
                      A deterministic skill's Output shows an exact shape (a
                      fenced block or a templates/ link).
  SKILL-4  links      relative links stay inside the plugin (an installed plugin
                      is copied alone into the host's cache, so `../../../../docs`
                      404s there); only sibling-skill SKILL.md links may leave it.
                      A backtick path into another plugin (`../../../polymath-x/…`)
                      fails too: installed plugins sit in versioned cache dirs.

Usage:
  check-skill-shape.py            # gate: exit 1 on any violation
  check-skill-shape.py --modes    # print `<plugin>:<skill> <mode>` per skill
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# The one sentence each mode carries, verbatim. Kept identical across skills so
# the model sees the same contract everywhere and drift is a lint failure.
MODES = {
    "deterministic": (
        "same inputs, same output. Follow the steps and the output shape "
        "exactly; compute with the named script or tool, never by estimate; "
        "add nothing the shape does not ask for."
    ),
    "analytical": (
        "judgment inside a fixed frame. Keep the output shape; every verdict "
        "cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never "
        "filled in."
    ),
    "generative": (
        "diverge before converging. Produce genuinely different options first "
        "(the obvious answer is one candidate, not the answer), then narrow "
        "with stated criteria."
    ),
}
MODE_LINE = re.compile(r"^\*\*Mode:\*\* ([a-z]+) — (.+)$", re.MULTILINE)

REQUIRED = [
    ("When to use", re.compile(r"^## When to use\s*$", re.MULTILINE)),
    ("Inputs", re.compile(r"^## Inputs\s*$", re.MULTILINE)),
    ("Procedure", re.compile(r"^## Procedure\b.*$", re.MULTILINE)),
    ("Output", re.compile(r"^## Output\b.*$", re.MULTILINE)),
    ("Quality bar / Anti-patterns",
     re.compile(r"^## (Quality bar|Anti-patterns)\b.*$", re.MULTILINE)),
]

LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
SIBLING = re.compile(r"^(\.\./)+([a-z0-9-]+/skills/)?[a-z0-9-]+/SKILL\.md$")
CROSS_PLUGIN_PATH = re.compile(r"`((?:\.\./){3,}polymath-[^`\s]*)`")


def output_section(body: str) -> str:
    m = re.search(r"^## Output\b.*?$(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def check(skill_md: pathlib.Path) -> tuple[list[str], str | None]:
    text = skill_md.read_text()
    m = re.match(r"^---\n.*?\n---\n(.*)$", text, re.DOTALL)
    body = m.group(1) if m else text
    errors: list[str] = []

    for label, rx in REQUIRED:
        if not rx.search(body):
            errors.append(f"SKILL-2: missing `## {label}` section")

    mode = None
    lines = MODE_LINE.findall(body)
    if len(lines) != 1:
        errors.append(f"SKILL-3: expected exactly one `**Mode:**` line, found {len(lines)}")
    else:
        mode, sentence = lines[0]
        if mode not in MODES:
            errors.append(f"SKILL-3: unknown mode {mode!r} (use {', '.join(MODES)})")
        elif sentence.strip() != MODES[mode]:
            errors.append(f"SKILL-3: `{mode}` mode sentence drifted from the canonical text")
        if mode == "deterministic":
            out = output_section(body)
            if "```" not in out and "templates/" not in out:
                errors.append("SKILL-3: deterministic skill's Output needs an exact shape (fenced block or templates/ link)")

    plugin_dir = skill_md.parents[2]
    for target in LINK.findall(body):
        if re.match(r"^[a-z]+:", target) or not target.startswith("../"):
            continue
        if SIBLING.match(target):
            continue
        resolved = (skill_md.parent / target).resolve()
        if plugin_dir.resolve() not in resolved.parents:
            errors.append(f"SKILL-4: link `{target}` leaves the plugin (dead once installed)")
    for target in CROSS_PLUGIN_PATH.findall(body):
        if not SIBLING.match(target):
            errors.append(f"SKILL-4: path `{target}` reaches into another plugin (versioned cache dirs break it)")
    return errors, mode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--modes", action="store_true", help="print each skill's declared mode")
    args = ap.parse_args()

    failures = 0
    counts = {m: 0 for m in MODES}
    for skill_md in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        sid = f"{skill_md.parents[2].name}:{skill_md.parent.name}"
        errors, mode = check(skill_md)
        if mode in counts:
            counts[mode] += 1
        if args.modes:
            print(f"{sid} {mode or '-'}")
            continue
        for e in errors:
            print(f"  ✗ {sid}: {e}")
        failures += bool(errors)
    if args.modes:
        return 0
    if failures:
        print(f"skill-shape: FAILED ({failures} skill(s))")
        return 1
    summary = ", ".join(f"{n} {m}" for m, n in counts.items())
    print(f"skill-shape: OK ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
