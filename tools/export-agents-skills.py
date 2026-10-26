#!/usr/bin/env python3
"""Export Polymath to a host-neutral agentskills.io bundle.

agentskills.io v1.0 (https://agentskills.io) is the open standard that
Claude Code, Codex CLI, Cursor, GitHub Copilot, VS Code, Gemini CLI,
Goose, OpenCode, Roo Code, JetBrains Junie, and other clients read.
Each client looks for SKILL.md files in one or more well-known
directories — `.agents/skills/`, `.codex/skills/`, `.cursor/skills/`,
`.claude/skills/`, `.github/skills/`. They all accept the same
SKILL.md shape: YAML frontmatter (`name` + `description`) + body.

This script materializes Polymath's portable surfaces into
`dist/agents-skills/`. Drop the contents into any of the well-known
directories in your project and the host harness will pick up every
directory that contains a SKILL.md.

What ports:
  - skills/<slug>/SKILL.md → dist/agents-skills/<plugin>-<slug>/SKILL.md
    (frontmatter `name` rewritten to `<plugin>-<slug>` so skills from
    different plugins never collide in the flat export).
  - commands/<slug>.md → dist/agents-skills/<plugin>-command-<slug>/SKILL.md
    (slash-command markdown converted to an invocable skill because slash
    command registries are host-specific).
  - agents/<slug>.md → dist/agents-skills/<plugin>-agent-<slug>/SKILL.md
    (forked-context subagent instructions converted to a normal skill; the
    target host may still run it in a forked context if it has that feature).
  - The skill's plugin templates/ directory, IF the SKILL.md body
    references it via `../../templates/`. The references are
    rewritten to `templates/` (relative to the exported skill).
  - All plugin templates, bin scripts, hook scripts, and MCP render templates
    are copied under `_polymath/` with manifest metadata and portable path contracts.

What cannot auto-activate everywhere:
  - hooks/hooks.json has no cross-agent event standard. The exporter emits
    normalized hook metadata plus scripts for host-specific adapters.
  - MCP is a protocol, but client discovery files differ — and the bundle
    never auto-registers anything. The exporter emits per-plugin server
    templates (`_polymath/mcp/<plugin>.servers.json`, canonical Claude-Code
    shape) and per-host renders under `_polymath/mcp/<host>/` (cursor,
    gemini-cli, opencode, codex, vscode) with each host's wrapper key and
    env-var syntax. Use `tools/mcp-registry.py scan` + `match` to reuse
    servers already registered in your host agent FIRST; render + install a
    template only when no host server matches and the user opts in — see
    docs/MCP-REUSE.md.
  - workflows/*.yaml remain driven by the bundled polymath-flow runner.

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
SUPPORT_DIR = "_polymath"
SUPPORT_ROOT = pathlib.Path(SUPPORT_DIR) / "support"
MCP_ROOT = pathlib.Path(SUPPORT_DIR) / "mcp"
HOOK_ROOT = pathlib.Path(SUPPORT_DIR) / "hooks"

FM_NAME = re.compile(r"^name:\s*([^\n]+)$", re.MULTILINE)
FM_DESCRIPTION = re.compile(r"^description:\s*([^\n]+)$", re.MULTILINE)
TEMPLATE_LINK = re.compile(r"\((\.\./\.\./templates/[^)]+)\)")
# Cross-skill link in the source tree: ../../../<plugin>/skills/<skill>/SKILL.md
SIBLING_LINK = re.compile(r"\((?:\.\./)+([a-z0-9-]+)/skills/([a-z0-9-]+)/SKILL\.md\)")
# Any remaining relative link with a `../` target — strip to plain label text.
OTHER_REL_LINK = re.compile(r"\[([^\]]+)\]\((?:\.\./)+[^)]*\)")
# A link target that is allowed to contain `../` after rewriting (sibling skill).
ALLOWED_REL_TARGET = re.compile(r"^\.\./[a-z0-9-]+/SKILL\.md$")
LINK_TARGET = re.compile(r"\]\(([^)]+)\)")
# Inline references to bundled support files, e.g. `../_polymath/support/<plugin>/bin/x.sh`.
# Captures the relative path up to the first whitespace/closing delimiter, so trailing
# script arguments and markdown punctuation are excluded.
BUNDLE_PATH_REF = re.compile(r"(?:\.\./)+_polymath/[^\s`)\]\"']+")
EXPORTED_CLAUDE_PATHS = [
    "CLAUDE_PLUGIN_ROOT",
    "CLAUDE_PLUGIN_DATA",
    "CLAUDE_CONFIG_DIR",
    "CLAUDE_PROJECT_DIR",
    "~/.claude/plugins/data",
    "$HOME/.claude/plugins/data",
]

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


def frontmatter_value(fm: str, pattern: re.Pattern[str]) -> str | None:
    m = pattern.search(fm)
    if not m:
        return None
    return m.group(1).strip().strip('"\'')


def rewrite_name(fm: str, namespaced: str) -> str:
    new_fm, n = FM_NAME.subn(f"name: {namespaced}", fm, count=1)
    if n == 0:
        # Inject a name when the source frontmatter has none (e.g. commands that
        # only carry a description). `fm` begins with the newline that follows
        # the opening `---` fence; preserve it so the writer's `---{new_fm}`
        # keeps the fence on its own line instead of producing `---name:`.
        new_fm = f"\nname: {namespaced}{fm}"
    return new_fm


# agentskills.io / Skills-API frontmatter allowlist. Strict hosts reject any
# other key, so Claude-only agent/command fields (disallowedTools, model,
# argument-hint, ...) must not leak into converted SKILL.md files.
PORTABLE_FM_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
FM_TOP_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):")


def portable_frontmatter(fm: str) -> str:
    """Drop top-level frontmatter keys (and their indented continuation lines)
    that are not in PORTABLE_FM_KEYS."""
    out: list[str] = []
    skipping = False
    for line in fm.split("\n"):
        m = FM_TOP_KEY.match(line)
        if m:
            skipping = m.group(1) not in PORTABLE_FM_KEYS
        elif line[:1] not in (" ", "\t", "-"):
            skipping = False
        if not skipping:
            out.append(line)
    return "\n".join(out)


def support_rel(plugin_name: str) -> str:
    return f"../{SUPPORT_ROOT.as_posix()}/{plugin_name}"


def rewrite_portable_paths(body: str, plugin_name: str) -> str:
    """Rewrite exported instructions away from Claude-owned path/env names.

    Source files may still carry Claude compatibility fallbacks because Claude
    Code is one supported host. Exported files should point at Polymath-owned
    paths that work when the bundle is dropped into `.agents/skills/`.
    """
    plugin_root = support_rel(plugin_name)
    replacements = {
        # Canonical source form: Claude Code substitutes the inner
        # ${CLAUDE_PLUGIN_ROOT} at skill-load time (the Bash tool never sees
        # plugin env vars), other hosts fall back to POLYMATH_PLUGIN_ROOT.
        "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}": plugin_root,
        "${POLYMATH_PLUGIN_ROOT:-$CLAUDE_PLUGIN_ROOT}": plugin_root,
        "${POLYMATH_PLUGIN_ROOT}": plugin_root,
        "$POLYMATH_PLUGIN_ROOT": plugin_root,
        "${CLAUDE_PLUGIN_ROOT}": plugin_root,
        "$CLAUDE_PLUGIN_ROOT": plugin_root,
        "${CLAUDE_PROJECT_DIR}": "${POLYMATH_PROJECT_DIR:-$PWD}",
        "$CLAUDE_PROJECT_DIR": "${POLYMATH_PROJECT_DIR:-$PWD}",
        "${CLAUDE_CONFIG_DIR}": "${POLYMATH_CONFIG_DIR}",
        "$CLAUDE_CONFIG_DIR": "$POLYMATH_CONFIG_DIR",
        "${CLAUDE_PLUGIN_DATA}": "${POLYMATH_DATA_DIR:-$HOME/.polymath/data}",
        "$CLAUDE_PLUGIN_DATA": "${POLYMATH_DATA_DIR:-$HOME/.polymath/data}",
        "$HOME/.claude/plugins/data": "${POLYMATH_DATA_DIR:-$HOME/.polymath/data}",
        "~/.claude/plugins/data": "${POLYMATH_DATA_DIR:-$HOME/.polymath/data}",
        "./.claude/polymath/workflows": "./.polymath/workflows",
        "$HOME/.claude/polymath/workflows": "$HOME/.polymath/workflows",
        "~/.claude/polymath/workflows": "~/.polymath/workflows",
        "CLAUDE_PLUGIN_DATA": "POLYMATH_DATA_DIR",
        "CLAUDE_CONFIG_DIR": "POLYMATH_CONFIG_DIR",
        "CLAUDE_PLUGIN_ROOT": "POLYMATH_PLUGIN_ROOT",
        "CLAUDE_PROJECT_DIR": "POLYMATH_PROJECT_DIR",
    }
    for old, new in replacements.items():
        body = body.replace(old, new)
    return body


def rewrite_body_links(body: str, plugin: pathlib.Path) -> tuple[str, list[str]]:
    """Rewrite links that point outside the flat exported skill directory."""
    referenced_templates: set[str] = set()

    def _sub(m: re.Match) -> str:
        target = m.group(1).replace("../../templates/", "templates/")
        referenced_templates.add(m.group(1).split("/")[-1])
        return f"({target})"

    new_body = TEMPLATE_LINK.sub(_sub, body)
    new_body = SIBLING_LINK.sub(
        lambda m: f"(../{m.group(1)}-{m.group(2)}/SKILL.md)", new_body
    )
    new_body = OTHER_REL_LINK.sub(lambda m: m.group(1), new_body)
    new_body = rewrite_portable_paths(new_body, plugin.name)
    return new_body, sorted(referenced_templates)


def ignore_generated(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n == "__pycache__" or n.endswith(".pyc")}


def copytree_clean(src: pathlib.Path, dest: pathlib.Path) -> None:
    shutil.copytree(src, dest, dirs_exist_ok=True, ignore=ignore_generated)


def iter_clean_files(root: pathlib.Path) -> list[pathlib.Path]:
    if not root.is_dir():
        return []
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
    )


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

    new_fm = rewrite_name(fm, namespaced)
    new_body, referenced_templates = rewrite_body_links(body, plugin)

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
            copytree_clean(src_sub, dest / sub)

    return {
        "kind": "skill",
        "exported_name": namespaced,
        "source_plugin": plugin_name,
        "source_skill": skill_name,
        "source_path": str(src_skill.relative_to(REPO)),
        "exported_path": str((dest / "SKILL.md").relative_to(out_root)),
        "templates_copied": copied,
        "portability": "claude-coupled" if reasons else "portable",
        "claudeCoupledReasons": reasons,
    }


def converted_banner(kind: str, source_name: str) -> str:
    if kind == "command":
        return (
            "<!-- portability:converted-command -->\n"
            f"> **Portability note.** This was a Claude slash command (`/{source_name}`). "
            "It is exported as a normal agentskills.io skill because command registries "
            "are host-specific. Follow the procedure below or invoke this skill by name.\n\n"
        )
    return (
        "<!-- portability:converted-agent -->\n"
        f"> **Portability note.** This was a Claude subagent (`{source_name}`). It is "
        "exported as a normal agentskills.io skill. If your host supports forked-context "
        "agents, run these instructions in that mode; otherwise use them in the current "
        "agent context.\n\n"
    )


def export_markdown_surface(
    md_path: pathlib.Path,
    plugin: pathlib.Path,
    out_root: pathlib.Path,
    *,
    kind: str,
) -> dict:
    slug = md_path.stem
    namespaced = f"{plugin.name}-{kind}-{slug}"
    dest = out_root / namespaced
    dest.mkdir(parents=True, exist_ok=True)

    text = md_path.read_text()
    fm, body, trailing = parse_frontmatter(text)
    new_fm = rewrite_name(portable_frontmatter(fm), namespaced)
    if not frontmatter_value(new_fm, FM_DESCRIPTION):
        new_fm += f"description: Portable {kind} exported from {plugin.name}:{slug}\n"
    new_body, _ = rewrite_body_links(body, plugin)
    reasons = coupling_reasons(new_body)
    if reasons:
        new_body = coupling_banner(reasons) + new_body
    new_body = converted_banner(kind, slug) + new_body
    (dest / "SKILL.md").write_text(f"---{new_fm}---\n{new_body}{trailing}")
    return {
        "kind": kind,
        "exported_name": namespaced,
        "source_plugin": plugin.name,
        "source_name": slug,
        "source_path": str(md_path.relative_to(REPO)),
        "exported_path": str((dest / "SKILL.md").relative_to(out_root)),
        "portability": "converted-coupled" if reasons else "converted",
        "claudeCoupledReasons": reasons,
    }


def rewrite_hook_command(command: str, plugin_name: str) -> str:
    rewritten = command.replace("${CLAUDE_PLUGIN_ROOT}", f"../support/{plugin_name}")
    # Shell-quoted strict form (the claude CLI's strict validator requires the
    # quoted placeholder); strip the quotes for the portable contract so the
    # run-hook dispatcher resolves the path directly.
    if rewritten.startswith('"') and rewritten.endswith('"'):
        return rewritten[1:-1]
    return rewritten


def export_hook_metadata(plugin: pathlib.Path, out_root: pathlib.Path) -> dict | None:
    hooks_path = plugin / "hooks" / "hooks.json"
    if not hooks_path.is_file():
        return None
    try:
        raw = json.loads(hooks_path.read_text())
    except json.JSONDecodeError as e:
        return {
            "source_plugin": plugin.name,
            "source_path": str(hooks_path.relative_to(REPO)),
            "error": f"invalid JSON: {e}",
        }
    events: list[dict] = []
    for event_name, groups in (raw.get("hooks") or {}).items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            matcher = group.get("matcher", "")
            for hook in group.get("hooks") or []:
                if not isinstance(hook, dict):
                    continue
                source_command = str(hook.get("command") or "")
                events.append(
                    {
                        "event": event_name,
                        "matcher": matcher,
                        "type": hook.get("type", "command"),
                        "sourceCommand": source_command,
                        "command": rewrite_hook_command(source_command, plugin.name),
                    }
                )
    dest = out_root / HOOK_ROOT / f"{plugin.name}.hooks.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "schemaVersion": 1,
        "source": str(hooks_path.relative_to(REPO)),
        "sourceHost": "claude-code",
        "portableContract": "event + matcher + command; adapt event names to the target host",
        "events": events,
    }
    dest.write_text(json.dumps(doc, indent=2) + "\n")
    return {
        "source_plugin": plugin.name,
        "source_path": str(hooks_path.relative_to(REPO)),
        "exported_path": str(dest.relative_to(out_root)),
        "eventCount": len(events),
        "events": sorted({e["event"] for e in events}),
    }


def export_mcp_config(plugin: pathlib.Path, out_root: pathlib.Path) -> tuple[dict | None, dict]:
    # Connector MCP server definitions live in mcp/servers.json — a RENDER
    # TEMPLATE (Claude-Code shape, env keys only), never an auto-registered
    # config. The exported copy keeps that status: it is documentation of
    # what the connector's server looks like, to be installed via
    # mcp-registry render only when the user opts in (their host agent's own
    # registered MCP servers are the default source).
    mcp_path = plugin / "mcp" / "servers.json"
    if not mcp_path.is_file():
        return None, {}
    doc = json.loads(mcp_path.read_text())
    servers = doc.get("mcpServers") if isinstance(doc, dict) else None
    servers = servers if isinstance(servers, dict) else {}
    dest = out_root / MCP_ROOT / f"{plugin.name}.servers.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"mcpServers": servers}, indent=2) + "\n")
    return (
        {
            "source_plugin": plugin.name,
            "source_path": str(mcp_path.relative_to(REPO)),
            "exported_path": str(dest.relative_to(out_root)),
            "servers": sorted(servers.keys()),
        },
        servers,
    )


def export_support_files(plugin: pathlib.Path, out_root: pathlib.Path) -> tuple[list[dict], list[dict]]:
    support = out_root / SUPPORT_ROOT / plugin.name
    templates: list[dict] = []
    scripts: list[dict] = []
    # data/ ships too: hooks and skills read it relative to the plugin root
    # (route-hint.py / event-trigger.py → data/route-signals.json, the flows
    # SessionStart index, run-workflow's workflow-detect.json). Without it the
    # bundled hook dispatcher runs against a missing table.
    for sub in ("templates", "bin", "hooks", "data"):
        src = plugin / sub
        if not src.is_dir():
            continue
        dest = support / sub
        copytree_clean(src, dest)
        if sub == "data":
            continue
        for path in iter_clean_files(src):
            entry = {
                "source_plugin": plugin.name,
                "source_path": str(path.relative_to(REPO)),
                "exported_path": str((dest / path.relative_to(src)).relative_to(out_root)),
            }
            if sub == "templates":
                templates.append(entry)
            else:
                scripts.append(entry)

    # Mirror each skill's scripts/ and references/ under support/skills/<skill>/
    # so that `${POLYMATH_PLUGIN_ROOT}/skills/<skill>/...` references resolve in
    # the bundle — including cross-skill references (e.g. initialize-project
    # invoking doctor's script). `${PLUGIN_ROOT}` maps to this support dir, so it
    # must faithfully mirror the plugin root, not only its top-level bin/.
    skills_dir = plugin / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            for sub in ("scripts", "references"):
                src = skill_dir / sub
                if not src.is_dir():
                    continue
                dest = support / "skills" / skill_dir.name / sub
                copytree_clean(src, dest)
                if sub == "scripts":
                    for path in iter_clean_files(src):
                        scripts.append({
                            "source_plugin": plugin.name,
                            "source_path": str(path.relative_to(REPO)),
                            "exported_path": str((dest / path.relative_to(src)).relative_to(out_root)),
                        })
    return templates, scripts


def portable_paths_contract() -> dict:
    return {
        "pluginRoot": {
            "description": "Bundled plugin files copied into the export.",
            "exportedPattern": f"{SUPPORT_ROOT.as_posix()}/<plugin>/",
            "env": "POLYMATH_PLUGIN_ROOT",
            "legacyClaudeEnv": "CLAUDE_PLUGIN_ROOT",
        },
        "dataRoot": {
            "description": "Machine-local mutable state for hooks, workflow runs, telemetry, and project context.",
            "env": "POLYMATH_DATA_DIR",
            "default": "~/.polymath/data",
            "legacyClaudeEnv": "CLAUDE_PLUGIN_DATA",
        },
        "configRoot": {
            "description": "User/team-level Polymath defaults.",
            "env": "POLYMATH_CONFIG_DIR",
            "default": "~/.polymath",
            "legacyClaudeEnv": "CLAUDE_CONFIG_DIR",
        },
        "projectRoot": {
            "description": "Current repository root. Project-local Polymath files live under .polymath/.",
            "env": "POLYMATH_PROJECT_DIR",
            "default": "$PWD",
            "legacyClaudeEnv": "CLAUDE_PROJECT_DIR",
        },
    }


def write_bundle_readme(out_root: pathlib.Path, manifest: dict) -> None:
    text = f"""# Polymath Portable Bundle

This directory is generated by `tools/export-agents-skills.py`.

Copy the bundle to an agentskills.io discovery directory such as
`.agents/skills/`. The top-level directories with `SKILL.md` files are
discoverable skills. `_polymath/` contains support files for host adapters.

## Inventory

- Skills: {manifest["skillCount"]}
- Converted commands: {manifest["commandCount"]}
- Converted subagents: {manifest["agentCount"]}
- Hook manifests: {manifest["hookCount"]}
- MCP server templates: {manifest["mcpServerCount"]}
- Templates: {manifest["templateCount"]}
- Scripts: {manifest["scriptCount"]}

## Portable Paths

- Data root: `${{POLYMATH_DATA_DIR:-$HOME/.polymath/data}}`
- Config root: `${{POLYMATH_CONFIG_DIR:-$HOME/.polymath}}`
- Project root: `${{POLYMATH_PROJECT_DIR:-$PWD}}`
- Plugin support files: `_polymath/support/<plugin>/`

## Hooks

Hooks ship with a runnable dispatcher. Wire your host's lifecycle events to:

    python3 _polymath/hooks/run-hook.py <EventName> [matcher]

It runs the matching commands from the normalized `_polymath/hooks/*.hooks.json`
manifests with the bundle root as the working directory and POLYMATH_* path
variables exported. MCP servers are NOT auto-registered anywhere: reuse the
host agent's own registered servers first (`_polymath/mcp/` holds render
templates and per-host fragments for the opt-in install path).
"""
    (out_root / "PORTABILITY.md").write_text(text)


HOOK_DISPATCHER = '''\
#!/usr/bin/env python3
"""Generic, host-agnostic hook dispatcher for the Polymath portable bundle.

Target hosts wire their lifecycle events to this script instead of needing a
bespoke adapter:

    python3 _polymath/hooks/run-hook.py <EventName> [matcher]

It reads every <plugin>.hooks.json beside it, runs the `command` of each event
whose name equals <EventName> and whose matcher (a regex over the optional
[matcher] argument, e.g. a tool name) matches, and forwards stdin to each
command. Commands run with the bundle root as the working directory and the
POLYMATH_* path variables exported. Scripts are launched by interpreter
(.py -> python3, .sh -> bash) so they need no execute bit. Exit code is the
worst child exit code; "no hook registered for this event" is success (0).
"""
import json
import os
import pathlib
import re
import subprocess
import sys

HOOKS_DIR = pathlib.Path(__file__).resolve().parent
BUNDLE_ROOT = HOOKS_DIR.parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: run-hook.py <EventName> [matcher]", file=sys.stderr)
        return 2
    event = sys.argv[1]
    subject = sys.argv[2] if len(sys.argv) > 2 else ""
    stdin_data = "" if sys.stdin.isatty() else sys.stdin.read()

    env = dict(os.environ)
    env.setdefault("POLYMATH_PROJECT_DIR", os.getcwd())
    env.setdefault("POLYMATH_DATA_DIR", os.path.expanduser("~/.polymath/data"))
    env.setdefault("POLYMATH_CONFIG_DIR", os.path.expanduser("~/.polymath"))

    worst = 0
    ran = 0
    for manifest in sorted(HOOKS_DIR.glob("*.hooks.json")):
        try:
            doc = json.loads(manifest.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for ev in doc.get("events", []):
            if ev.get("event") != event:
                continue
            matcher = ev.get("matcher") or ""
            if matcher and subject and not re.search(matcher, subject):
                continue
            command = ev.get("command") or ""
            cmd_path = (HOOKS_DIR / command).resolve()
            if not cmd_path.exists():
                print(f"run-hook: missing command {command}", file=sys.stderr)
                worst = max(worst, 1)
                continue
            if cmd_path.suffix == ".py":
                argv = [sys.executable, str(cmd_path)]
            elif cmd_path.suffix == ".sh":
                argv = ["bash", str(cmd_path)]
            else:
                argv = [str(cmd_path)]
            proc = subprocess.run(
                argv, cwd=str(BUNDLE_ROOT), env=env, input=stdin_data, text=True
            )
            worst = max(worst, proc.returncode)
            ran += 1
    return worst if ran else 0


if __name__ == "__main__":
    sys.exit(main())
'''


def emit_hook_dispatcher(out_root: pathlib.Path) -> None:
    """Ship a runnable, host-agnostic hook dispatcher so exported hooks are
    executable on any host that can call a command on a lifecycle event — not
    merely portable metadata."""
    dest = out_root / HOOK_ROOT / "run-hook.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(HOOK_DISPATCHER)
    dest.chmod(0o755)


def verify_host_load(out_root: pathlib.Path) -> tuple[dict, list[str]]:
    """Reference agentskills.io host: load every exported skill the way a
    compliant host would (parse frontmatter, require name + description) and
    resolve every relative reference to a file that exists in the bundle.

    This is a stand-in for a live host: it proves the deployed bundle is
    loadable and self-contained, short of installing each proprietary agent."""
    problems: list[str] = []
    loaded = 0
    resolved = 0
    for skill_md in sorted(out_root.glob("*/SKILL.md")):
        rel = skill_md.relative_to(out_root)
        text = skill_md.read_text()
        fm, body, _ = parse_frontmatter(text)
        if not frontmatter_value(fm, FM_NAME) or not frontmatter_value(fm, FM_DESCRIPTION):
            problems.append(f"{rel}: host cannot load (missing name or description)")
            continue
        loaded += 1
        # Relative markdown links must resolve to a file in the bundle.
        for target in LINK_TARGET.findall(body):
            link = target.split("#", 1)[0].strip()
            if not link or "://" in link:
                continue
            if not (link.startswith("./") or link.startswith("../")):
                continue
            if (skill_md.parent / link).resolve().exists():
                resolved += 1
            else:
                problems.append(f"{rel}: dangling reference `{target}` (host would 404)")
        # Bundled scripts/templates are usually named inline (in backticks) as
        # `_polymath/...` paths, not markdown links. A skill that tells the user
        # to run a script that isn't in the bundle is not self-contained.
        for token in BUNDLE_PATH_REF.findall(body):
            if (skill_md.parent / token).resolve().exists():
                resolved += 1
            else:
                problems.append(
                    f"{rel}: references bundle path `{token}` that does not exist (not self-contained)"
                )
    return {"loaded": loaded, "resolvedRefs": resolved}, problems


def lint_output(out_root: pathlib.Path) -> list[str]:
    """Fail-closed check over the written bundle: no dead `../` links survive,
    every Claude-coupled body carries the banner marker, and exported
    instructions do not retain Claude-owned path variables."""
    problems: list[str] = []
    for skill_md in sorted(out_root.glob("*/SKILL.md")):
        text = skill_md.read_text()
        rel = skill_md.relative_to(out_root)
        # The opening YAML fence must stand alone on the first line; a glued
        # `---name:` is not a valid document marker and breaks frontmatter
        # parsing on agentskills.io hosts.
        if not text.startswith("---\n"):
            problems.append(f"{rel}: malformed frontmatter fence (first line is not `---`)")
        elif not frontmatter_value(parse_frontmatter(text)[0], FM_NAME):
            problems.append(f"{rel}: exported SKILL.md has no `name` in frontmatter")
        for target in LINK_TARGET.findall(text):
            if "../" in target and not ALLOWED_REL_TARGET.match(target):
                problems.append(f"{rel}: unrewritten relative link `{target}`")
        if coupling_reasons(text) and COUPLED_MARKER not in text:
            problems.append(f"{rel}: depends on a Claude-only surface but has no portability banner")
        for token in EXPORTED_CLAUDE_PATHS:
            if token in text:
                problems.append(f"{rel}: exported instructions retain Claude-specific path token `{token}`")
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
    for key, collection in (("commandCount", "commands"), ("agentCount", "agents")):
        items = manifest.get(collection, [])
        if manifest.get(key) != len(items):
            problems.append(f"manifest {key} {manifest.get(key)} != {len(items)} {collection} listed")
    for key in ("hooks", "mcpServers", "templates", "scripts", "paths"):
        if key not in manifest:
            problems.append(f"manifest missing {key}")
    required = {"exported_name", "source_plugin", "source_skill", "portability"}
    for e in skills:
        missing = required - e.keys()
        if missing:
            problems.append(
                f"manifest skill entry {e.get('exported_name', '?')} missing keys: {sorted(missing)}"
            )
            break
    for collection in ("commands", "agents"):
        required_converted = {"exported_name", "source_plugin", "source_name", "source_path", "exported_path"}
        for e in manifest.get(collection, []):
            missing = required_converted - e.keys()
            if missing:
                problems.append(
                    f"manifest {collection} entry {e.get('exported_name', '?')} missing keys: {sorted(missing)}"
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
    parser.add_argument("--install", type=pathlib.Path, default=None, metavar="DIR",
                        help="After exporting, copy the bundle into DIR (a target "
                             "host's agentskills.io discovery directory, e.g. "
                             ".agents/skills) and host-load-verify the deployed copy.")
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
    command_entries: list[dict] = []
    agent_entries: list[dict] = []
    hook_entries: list[dict] = []
    mcp_entries: list[dict] = []
    all_mcp_servers: dict = {}
    template_entries: list[dict] = []
    script_entries: list[dict] = []
    for plugin in sorted(PLUGINS_DIR.iterdir()):
        if not plugin.is_dir():
            continue
        templates, scripts = export_support_files(plugin, out_root)
        template_entries.extend(templates)
        script_entries.extend(scripts)

        hook_entry = export_hook_metadata(plugin, out_root)
        if hook_entry is not None:
            hook_entries.append(hook_entry)

        mcp_entry, mcp_servers = export_mcp_config(plugin, out_root)
        if mcp_entry is not None:
            mcp_entries.append(mcp_entry)
            for server, config in mcp_servers.items():
                all_mcp_servers[server] = config

        skills_dir = plugin / "skills"
        if skills_dir.is_dir():
            for skill_dir in sorted(skills_dir.iterdir()):
                if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
                    continue
                entry = export_skill(skill_dir, plugin, out_root)
                entries.append(entry)

        commands_dir = plugin / "commands"
        if commands_dir.is_dir():
            for md_path in sorted(commands_dir.glob("*.md")):
                command_entries.append(
                    export_markdown_surface(md_path, plugin, out_root, kind="command")
                )

        agents_dir = plugin / "agents"
        if agents_dir.is_dir():
            for md_path in sorted(agents_dir.glob("*.md")):
                if md_path.name.endswith(".routing.yaml"):
                    continue
                agent_entries.append(
                    export_markdown_surface(md_path, plugin, out_root, kind="agent")
                )

    if all_mcp_servers:
        # Aggregate template: kept Claude-Code-shaped for reference only — a
        # paste-ready auto-registered aggregate would defeat the reuse-first
        # model. Per-host renders remain available so an OPT-IN install is a
        # copy, not a translation exercise.
        aggregate = out_root / MCP_ROOT / "servers.json"
        aggregate.parent.mkdir(parents=True, exist_ok=True)
        aggregate.write_text(json.dumps({"mcpServers": all_mcp_servers}, indent=2) + "\n")
        # Per-host renders: the canonical template is Claude-Code-shaped
        # (mcpServers + ${VAR:-} expansion). Other hosts need their own
        # wrapper key, env syntax, and command shape. mcp-registry.py owns
        # the per-host rendering; the exporter just materializes it.
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "mcp_registry", REPO / "tools" / "mcp-registry.py"
            )
            mcp_registry = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mcp_registry)
            for host in mcp_registry.HOSTS:
                if host == "claude-code":
                    continue  # the aggregate itself is the claude-code render
                frag = mcp_registry.render_fragment(all_mcp_servers, host)
                if frag is None:
                    continue
                dest = out_root / MCP_ROOT / host
                dest.mkdir(parents=True, exist_ok=True)
                if host == "codex":
                    (dest / "mcp.toml").write_text(frag + "\n", encoding="utf-8")
                else:
                    (dest / "mcp.json").write_text(
                        json.dumps(frag, indent=2) + "\n", encoding="utf-8"
                    )
        except Exception as e:
            print(f"export-agents-skills: warning: per-host MCP renders skipped ({e})", file=sys.stderr)

    # Ship the runnable hook dispatcher so hooks are executable on any host,
    # not just portable JSON that needs a bespoke per-host adapter.
    emit_hook_dispatcher(out_root)

    portable_count = sum(1 for e in entries if e["portability"] == "portable")
    coupled_count = len(entries) - portable_count
    manifest = {
        "spec": "agentskills.io",
        "specVersion": "1.0",
        "marketplace": "polymath",
        "bundle": "polymath-portable",
        "bundleVersion": 2,
        "skillCount": len(entries),
        "commandCount": len(command_entries),
        "agentCount": len(agent_entries),
        "discoverableSkillCount": len(entries) + len(command_entries) + len(agent_entries),
        "portableCount": portable_count,
        "claudeCoupledCount": coupled_count,
        "hookCount": len(hook_entries),
        "mcpConfigCount": len(mcp_entries),
        "mcpServerCount": sum(len(e.get("servers", [])) for e in mcp_entries),
        "templateCount": len(template_entries),
        "scriptCount": len(script_entries),
        "skills": entries,
        "commands": command_entries,
        "agents": agent_entries,
        "hooks": hook_entries,
        "mcpServers": mcp_entries,
        "templates": template_entries,
        "scripts": script_entries,
        "paths": portable_paths_contract(),
        "hostAdapterRequired": {
            "rationale": "These surfaces are exported as files/metadata, but target hosts do not share one discovery or event standard.",
            "surfaces": [
                "hooks/hooks.json (normalized under _polymath/hooks/); run via the bundled _polymath/hooks/run-hook.py dispatcher — the host only needs to call it on its own lifecycle events",
                "mcp/servers.json (templates under _polymath/mcp/<plugin>.servers.json + per-host renders under _polymath/mcp/<host>/ for cursor, gemini-cli, opencode, codex, vscode; claude-code uses the template shape) — render inputs, installed only when the user opts in; reuse the host's registered MCP servers first",
                "workflows/*.yaml (run through _polymath/support/polymath-flows/bin/polymath-flow)",
            ],
            "hookDispatcher": "_polymath/hooks/run-hook.py",
        },
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_bundle_readme(out_root, manifest)

    print(
        f"export-agents-skills: wrote {len(entries)} skill(s), "
        f"{len(command_entries)} command skill(s), {len(agent_entries)} agent skill(s) "
        f"to {display(out_root)}"
    )
    print(f"manifest:              {display(out_root / 'manifest.json')}")
    print(f"portability:           {portable_count} portable, {coupled_count} Claude-coupled (bannered)")
    print(
        "support:               "
        f"{len(hook_entries)} hook manifest(s), "
        f"{sum(len(e.get('servers', [])) for e in mcp_entries)} MCP template server(s), "
        f"{len(template_entries)} template(s), {len(script_entries)} script(s)"
    )

    problems = lint_output(out_root)
    problems += validate_manifest(manifest)

    # Reference-host load: prove every exported skill is loadable and that every
    # relative reference resolves to a real file in the bundle.
    load_stats, load_problems = verify_host_load(out_root)
    problems += load_problems

    # Deploy to a target host's discovery directory and verify the copy in place.
    install_stats = None
    if args.install is not None and not problems:
        install_dir = args.install.resolve()
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        if install_dir.exists():
            shutil.rmtree(install_dir)
        shutil.copytree(out_root, install_dir)
        deployed_stats, deployed_problems = verify_host_load(install_dir)
        problems += [f"(installed) {p}" for p in deployed_problems]
        install_stats = (install_dir, deployed_stats)

    if args.check:
        shutil.rmtree(out_root, ignore_errors=True)
    if problems:
        for p in problems:
            print(f"::error::export lint: {p}", file=sys.stderr)
        print(f"\nexport-agents-skills: {len(problems)} portability problem(s)", file=sys.stderr)
        return 1
    print(
        f"host-load verify:      OK — reference agentskills.io host loaded "
        f"{load_stats['loaded']}/{manifest['discoverableSkillCount']} skill(s), "
        f"resolved {load_stats['resolvedRefs']} relative reference(s), 0 dangling"
    )
    if install_stats is not None:
        idir, ddeployed = install_stats
        print(
            f"installed:             {display(idir)} — deployed copy host-load "
            f"verified ({ddeployed['loaded']} skill(s))"
        )
    if args.check:
        print(
            f"export --check:        OK — {manifest['discoverableSkillCount']} "
            "discoverable skill(s) export cleanly, manifest valid"
        )
    else:
        print("export lint:           OK — no dead relative links; coupled skills bannered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
