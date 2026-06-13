#!/usr/bin/env python3
"""Export every Polymath skill to the agentskills.io v1.0 layout.

agentskills.io v1.0 (https://agentskills.io) is the open standard that
Claude Code, Codex CLI, Cursor, GitHub Copilot, VS Code, Gemini CLI,
Goose, OpenCode, Roo Code, JetBrains Junie, and other clients read.
Each client looks for SKILL.md files in one or more well-known
directories — `.agents/skills/`, `.codex/skills/`, `.cursor/skills/`,
`.claude/skills/`, `.github/skills/`. They all accept the same
SKILL.md shape: YAML frontmatter (`name` + `description`) + body.

This script materializes every Polymath skill into a portable bundle
under `dist/agents-skills/`. Drop the contents into any of the
well-known directories in your project and the host harness will pick
them up.

What ports:
  - skills/<slug>/SKILL.md → dist/agents-skills/<plugin>-<slug>/SKILL.md
    (frontmatter `name` rewritten to `<plugin>-<slug>` so skills from
    different plugins never collide in the flat export).
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
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO / "plugins"
DEFAULT_OUT = REPO / "dist" / "agents-skills"
COUPLING_BASELINE = REPO / "registry" / "coupling-baseline.json"

FM_NAME = re.compile(r"^name:\s*([^\n]+)$", re.MULTILINE)
TEMPLATE_LINK = re.compile(r"\((\.\./\.\./templates/[^)]+)\)")
# Cross-skill link in the source tree: ../../../<plugin>/skills/<skill>/SKILL.md
SIBLING_LINK = re.compile(r"\((?:\.\./)+([a-z0-9-]+)/skills/([a-z0-9-]+)/SKILL\.md\)")
# Any remaining relative link with a `../` target — strip to plain label text.
OTHER_REL_LINK = re.compile(r"\[([^\]]+)\]\((?:\.\./)+[^)]*\)")
# A link target that is allowed to contain `../` after rewriting (sibling skill).
ALLOWED_REL_TARGET = re.compile(r"^\.\./[a-z0-9-]+/SKILL\.md$")
LINK_TARGET = re.compile(r"\]\(([^)]+)\)")

# Tokens whose presence means the skill body instructs the agent to use a
# Claude-Code-only surface that a generic agentskills.io host does not provide.
CLAUDE_COUPLING = [
    (re.compile(r"\bMCP\b|mcp__|MCP server", re.IGNORECASE), "MCP server"),
    (re.compile(r"SessionStart|CLAUDE_PLUGIN_DATA|project-context\.json"), "SessionStart hook / plugin data"),
    (re.compile(r"\brun-workflow\b|polymath-flow\b|/polymath-flows:"), "polymath-flows runner"),
    (re.compile(r"hooks/scripts/"), "hook script path"),
]
COUPLED_MARKER = "<!-- portability:claude-coupled -->"


def coupling_reasons(body: str) -> list[str]:
    """Return the distinct Claude-only surfaces this skill body depends on."""
    reasons: list[str] = []
    for rx, label in CLAUDE_COUPLING:
        if rx.search(body) and label not in reasons:
            reasons.append(label)
    return reasons


def coupling_banner(reasons: list[str]) -> str:
    joined = ", ".join(reasons)
    return (
        f"{COUPLED_MARKER}\n"
        f"> **Portability note (exported from Polymath).** This skill references "
        f"Claude Code surfaces ({joined}) that a generic agentskills.io host does "
        f"not provide. Steps that depend on them will not run here — use this skill "
        f"on Claude Code, or substitute your harness's equivalent tool. See "
        f"PORTABILITY.md in the Polymath repo.\n\n"
    )


# ---------------------------------------------------------------------------
# COUPLING-1 — occurrence ratchet over the catalog's Claude-coupling
# ---------------------------------------------------------------------------


def coupling_occurrences() -> tuple[int, list[tuple[str, list[str]]]]:
    """Catalog-wide Claude-coupling: the total count of distinct
    skill×surface dependencies, plus a per-coupled-skill breakdown. Counts the
    same `coupling_reasons` the exporter banners on, so the ratchet and the
    export banner can never disagree about what is coupled."""
    breakdown: list[tuple[str, list[str]]] = []
    total = 0
    for plugin in sorted(PLUGINS_DIR.iterdir()):
        skills_dir = plugin / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_dir in sorted(skills_dir.iterdir()):
            md = skill_dir / "SKILL.md"
            if not md.is_file():
                continue
            reasons = coupling_reasons(md.read_text(errors="ignore"))
            if reasons:
                breakdown.append((f"{plugin.name}:{skill_dir.name}", reasons))
                total += len(reasons)
    return total, breakdown


def _coupling_problems(current: int, ceiling: int) -> list[str]:
    """The ratchet is one-directional: coupling may shrink freely but may not
    grow past the frozen ceiling without a conscious baseline bump."""
    if current > ceiling:
        return [
            f"Claude-coupling occurrences rose to {current}, above the ratchet "
            f"ceiling {ceiling} (registry/coupling-baseline.json) — make the new "
            f"reference portable, or consciously raise the ceiling to accept the "
            f"portability cost"
        ]
    return []


def coupling_ratchet_check() -> int:
    try:
        ceiling = int(json.loads(COUPLING_BASELINE.read_text())["coupling_occurrences_max"])
    except Exception as e:
        print(f"coupling-ratchet: cannot read {COUPLING_BASELINE}: {e}", file=sys.stderr)
        return 1
    total, breakdown = coupling_occurrences()
    problems = _coupling_problems(total, ceiling)
    if problems:
        for p in problems:
            print(f"::error::COUPLING-1: {p}", file=sys.stderr)
        print("\ncoupled skills:", file=sys.stderr)
        for name, reasons in breakdown:
            print(f"  {name}: {', '.join(reasons)}", file=sys.stderr)
        return 1
    note = ""
    if total < ceiling:
        note = (
            f" — below ceiling; lower coupling_occurrences_max to {total} in "
            f"registry/coupling-baseline.json to lock the reduction"
        )
    print(
        f"coupling-ratchet: OK — {total} Claude-coupling occurrence(s) across "
        f"{len(breakdown)} skill(s), ceiling {ceiling}{note}"
    )
    return 0


def coupling_ratchet_self_test() -> int:
    checks = [
        ("growth above ceiling rejected", bool(_coupling_problems(11, 10))),
        ("count at ceiling accepted", not _coupling_problems(10, 10)),
        ("count below ceiling accepted", not _coupling_problems(7, 10)),
        ("rejection names the ceiling", any("ceiling 10" in p for p in _coupling_problems(11, 10))),
    ]
    failures = 0
    for label, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        failures += 0 if ok else 1
    if failures:
        print(f"coupling-ratchet --self-test FAILED ({failures} check(s))", file=sys.stderr)
        return 1
    print("coupling-ratchet --self-test: ratchet correctly rejects synthetic coupling growth")
    return 0


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

    # Rewrite cross-skill links to the flat exported sibling-dir form:
    # ../../../<plugin>/skills/<skill>/SKILL.md  →  ../<plugin>-<skill>/SKILL.md
    new_body = SIBLING_LINK.sub(
        lambda m: f"(../{m.group(1)}-{m.group(2)}/SKILL.md)", new_body
    )
    # Any remaining `../` link (to registry/, docs/, …) does not exist in the flat
    # bundle — drop the link, keep the label as plain text so nothing 404s.
    new_body = OTHER_REL_LINK.sub(lambda m: m.group(1), new_body)

    # Prepend an environment-requirements banner when the body depends on a
    # Claude-Code-only surface, so the exported file is honest on its own.
    reasons = coupling_reasons(new_body)
    if reasons:
        new_body = coupling_banner(reasons) + new_body

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
        "portability": "claude-coupled" if reasons else "portable",
        "claudeCoupledReasons": reasons,
    }


def lint_output(out_root: pathlib.Path) -> list[str]:
    """Fail-closed check over the written bundle: no dead `../` links survive,
    and every Claude-coupled body carries the banner marker."""
    problems: list[str] = []
    for skill_md in sorted(out_root.glob("*/SKILL.md")):
        text = skill_md.read_text()
        rel = skill_md.relative_to(out_root)
        for target in LINK_TARGET.findall(text):
            if "../" in target and not ALLOWED_REL_TARGET.match(target):
                problems.append(f"{rel}: unrewritten relative link `{target}`")
        if coupling_reasons(text) and COUPLED_MARKER not in text:
            problems.append(f"{rel}: depends on a Claude-only surface but has no portability banner")
    return problems


def validate_manifest(manifest: dict) -> list[str]:
    """Structural checks on the emitted manifest (used by --check)."""
    problems: list[str] = []
    if manifest.get("spec") != "agentskills.io":
        problems.append(f"manifest spec is {manifest.get('spec')!r}, expected 'agentskills.io'")
    if not manifest.get("specVersion"):
        problems.append("manifest missing specVersion")
    skills = manifest.get("skills", [])
    if manifest.get("skillCount") != len(skills):
        problems.append(f"manifest skillCount {manifest.get('skillCount')} != {len(skills)} skills listed")
    if manifest.get("portableCount", 0) + manifest.get("claudeCoupledCount", 0) != len(skills):
        problems.append("manifest portableCount + claudeCoupledCount != skillCount")
    required = {"exported_name", "source_plugin", "source_skill", "portability"}
    for e in skills:
        missing = required - e.keys()
        if missing:
            problems.append(
                f"manifest skill entry {e.get('exported_name', '?')} missing keys: {sorted(missing)}"
            )
            break
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT,
                        help="Output directory (default: dist/agents-skills)")
    parser.add_argument("--clean", action="store_true",
                        help="Remove the output directory before exporting "
                             "(refused outside dist/ unless --force).")
    parser.add_argument("--force", action="store_true",
                        help="Permit --clean to remove a path outside dist/.")
    parser.add_argument("--check", action="store_true",
                        help="Build into a throwaway temp dir, validate the "
                             "manifest, and clean up. Touches nothing in dist/. "
                             "Exit non-zero on any export/lint/manifest problem.")
    parser.add_argument("--coupling-ratchet", action="store_true",
                        help="COUPLING-1: assert catalog-wide Claude-coupling "
                             "occurrences do not exceed the ratchet ceiling in "
                             "registry/coupling-baseline.json. Exports nothing.")
    parser.add_argument("--self-test", action="store_true",
                        help="With --coupling-ratchet: prove the ratchet rejects "
                             "synthetic coupling growth.")
    args = parser.parse_args()

    if args.coupling_ratchet:
        return coupling_ratchet_self_test() if args.self_test else coupling_ratchet_check()

    def display(p: pathlib.Path) -> pathlib.Path | str:
        try:
            return p.relative_to(REPO)
        except ValueError:
            return p

    # --check builds into a throwaway temp dir and validates the result, so it
    # never touches dist/ and leaves nothing behind.
    if args.check:
        out_root = pathlib.Path(tempfile.mkdtemp(prefix="polymath-export-check-"))
    else:
        # --clean does a recursive delete; refuse to point it anywhere but dist/
        # (the only directory this tool owns) unless the caller forces it.
        # Without this guard a stray `--out` would silently rmtree an unrelated tree.
        out_root = args.out.resolve()
        dist_root = (REPO / "dist").resolve()
        if args.clean and out_root.exists():
            within_dist = out_root == dist_root or out_root.is_relative_to(dist_root)
            if not within_dist and not args.force:
                print(
                    f"export-agents-skills: refusing to --clean {display(out_root)}: "
                    f"not under {display(dist_root)}/ — re-run with --force to override.",
                    file=sys.stderr,
                )
                return 2
            print(f"export-agents-skills: removing {display(out_root)}")
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

    portable_count = sum(1 for e in entries if e["portability"] == "portable")
    coupled_count = len(entries) - portable_count
    manifest = {
        "spec": "agentskills.io",
        "specVersion": "1.0",
        "marketplace": "polymath",
        "skillCount": len(entries),
        "portableCount": portable_count,
        "claudeCoupledCount": coupled_count,
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
                "registry/schemas/artifacts/*.json",
                ".polymath/project.yaml + capabilities.yaml",
            ],
        },
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"export-agents-skills: wrote {len(entries)} skill(s) to {display(out_root)}")
    print(f"manifest:              {display(out_root / 'manifest.json')}")
    print(f"portability:           {portable_count} portable, {coupled_count} Claude-coupled (bannered)")

    problems = lint_output(out_root)
    problems += validate_manifest(manifest)
    if args.check:
        shutil.rmtree(out_root, ignore_errors=True)
    if problems:
        for p in problems:
            print(f"::error::export lint: {p}", file=sys.stderr)
        print(f"\nexport-agents-skills: {len(problems)} portability problem(s)", file=sys.stderr)
        return 1
    if args.check:
        print(f"export --check:        OK — {len(entries)} skill(s) export cleanly, manifest valid")
    else:
        print("export lint:           OK — no dead relative links; coupled skills bannered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
