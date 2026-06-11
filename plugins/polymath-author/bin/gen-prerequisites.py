#!/usr/bin/env python3
"""gen-prerequisites — prerequisites-checklist generator.

Turns the `setup` block of `.polymath/project.yaml` (context_sources,
required_tools, environment, first_steps) into a human onboarding
checklist, so the prose a new contributor (or coding agent) needs is
generated from the same config the agents already consume — never
hand-maintained in parallel.

Usage:
  gen-prerequisites.py [--cwd DIR] [--out FILE] [--check]

  --out FILE   write the checklist there (default: stdout)
  --check      run each required_tools[].check command and annotate the
               checklist with PASS/FAIL instead of empty checkboxes;
               exit 1 when any REQUIRED tool fails (CI-able)

Input resolution: `.polymath/project.yaml` from --cwd (or cwd) walking up
to the repo boundary, parsed with PyYAML when available; otherwise the
newest polymath-core project-context snapshot (the loader's JSON) is used.
Environment variable VALUES are never read or printed — names and
purposes only, per the schema's sensitivity contract.

Exit codes: 0 ok, 1 --check found a failing required tool, 2 no usable
project config / setup block.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys


def _find_project_root(start: pathlib.Path) -> pathlib.Path | None:
    here = start.resolve()
    for d in (here, *here.parents):
        try:
            if (d / ".polymath" / "project.yaml").is_file():
                return d
            if (d / ".git").exists():
                return None
        except OSError:
            return None
    return None


def _load_config(root: pathlib.Path) -> dict | None:
    path = root / ".polymath" / "project.yaml"
    try:
        import yaml  # type: ignore

        doc = yaml.safe_load(path.read_text())
        return doc if isinstance(doc, dict) else None
    except ImportError:
        pass
    except Exception:
        return None
    # No PyYAML: fall back to the loader's resolved snapshot (JSON).
    candidates: list[pathlib.Path] = []
    env = os.environ.get("CLAUDE_PLUGIN_DATA")
    if env:
        base = pathlib.Path(env)
        candidates.append(base / "polymath-core" / "project-context.json")
        candidates.extend(base.parent.glob("*/polymath-core/project-context.json"))
    home = pathlib.Path.home() / ".claude" / "plugins" / "data"
    candidates.append(home / "polymath-core" / "project-context.json")
    candidates.extend(home.glob("polymath-core-*/polymath-core/project-context.json"))
    existing = [c for c in candidates if c.is_file()]
    if not existing:
        return None
    newest = max(existing, key=lambda p: p.stat().st_mtime)
    try:
        doc = json.loads(newest.read_text())
        return doc if isinstance(doc, dict) else None
    except Exception:
        return None


def _run_check(command: str) -> bool:
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return proc.returncode == 0
    except Exception:
        return False


def render(config: dict, *, run_checks: bool) -> tuple[str, bool]:
    """Render the checklist. Returns (markdown, any_required_tool_failed)."""
    setup = config.get("setup") or {}
    name = (config.get("project") or {}).get("name") or "this project"
    lines: list[str] = [
        f"# Prerequisites — {name}",
        "",
        "Generated from the `setup` block of `.polymath/project.yaml` by",
        "`polymath-author` (`bin/gen-prerequisites.py`). Edit the setup block",
        "and re-generate; don't hand-edit this file.",
    ]
    any_required_failed = False

    sources = setup.get("context_sources") or []
    if sources:
        lines += ["", "## Read these first", ""]
        lines += [f"- [ ] `{s}`" for s in sources if isinstance(s, str)]

    tools = setup.get("required_tools") or []
    if tools:
        lines += ["", "## Tools", ""]
        for tool in tools:
            if not isinstance(tool, dict) or not tool.get("name"):
                continue
            required = tool.get("required", True)
            label = str(tool["name"])
            if tool.get("version"):
                label += f" {tool['version']}"
            suffix = "" if required else " *(optional)*"
            check = tool.get("check")
            if run_checks and check:
                ok = _run_check(str(check))
                box = "[x] PASS" if ok else "[ ] FAIL"
                if not ok and required:
                    any_required_failed = True
                lines.append(f"- {box} — {label}{suffix} — `{check}`")
            elif check:
                lines.append(f"- [ ] {label}{suffix} — verify with `{check}`")
            else:
                lines.append(f"- [ ] {label}{suffix}")

    env_vars = setup.get("environment") or []
    if env_vars:
        lines += ["", "## Environment", ""]
        for var in env_vars:
            if not isinstance(var, dict) or not var.get("name"):
                continue
            required = var.get("required", False)
            sensitive = var.get("sensitive", True)
            notes = []
            if var.get("purpose"):
                notes.append(str(var["purpose"]))
            notes.append("required" if required else "optional")
            if sensitive:
                notes.append("sensitive — set locally, never commit the value")
            lines.append(f"- [ ] `{var['name']}` — {'; '.join(notes)}")

    steps = setup.get("first_steps") or []
    if steps:
        lines += ["", "## First steps", ""]
        lines += [
            f"{i}. [ ] {s}" for i, s in enumerate(
                (s for s in steps if isinstance(s, str)), start=1
            )
        ]

    if len(lines) <= 5:
        lines += [
            "",
            "_The setup block is empty — fill in `setup.context_sources`,",
            "`setup.required_tools`, `setup.environment`, and",
            "`setup.first_steps` in `.polymath/project.yaml` first",
            "(`/polymath-core:init-project` infers them)._",
        ]
    return "\n".join(lines) + "\n", any_required_failed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cwd", help="resolve the project from here (default: cwd)")
    ap.add_argument("--out", help="write the checklist to this file (default: stdout)")
    ap.add_argument(
        "--check",
        action="store_true",
        help="run required_tools[].check commands; exit 1 if a required tool fails",
    )
    args = ap.parse_args(argv)

    root = _find_project_root(pathlib.Path(args.cwd) if args.cwd else pathlib.Path.cwd())
    if root is None:
        print(
            "gen-prerequisites: no .polymath/project.yaml found here "
            "(run /polymath-core:init-project first)",
            file=sys.stderr,
        )
        return 2
    config = _load_config(root)
    if config is None:
        print(
            "gen-prerequisites: could not parse the project config "
            "(install pyyaml, or start one session so the loader writes its snapshot)",
            file=sys.stderr,
        )
        return 2

    text, failed = render(config, run_checks=args.check)
    if args.out:
        out = pathlib.Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"wrote {out}")
    else:
        sys.stdout.write(text)
    return 1 if (args.check and failed) else 0


if __name__ == "__main__":
    sys.exit(main())
