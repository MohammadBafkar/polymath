#!/usr/bin/env python3
"""Read .polymath/project.yaml, validate the minimal-subset shape, and emit
the resolved context as JSON to ${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json.

This script is invoked by polymath-core's SessionStart hook. It runs quietly
when no project file exists (exit 0, no output) and surfaces a one-line
summary to stdout when one does — surfaced text becomes part of the model's
opening context per the Claude Code SessionStart hook contract.

Inputs:
  Searched in order, first hit wins:
    1. ./.polymath/project.yaml (project, repo-root)
    2. ${CLAUDE_CONFIG_DIR}/polymath/project.yaml (user/team default)
    3. ~/.polymath/project.yaml (last-resort user default)
  Overlay (optional, machine-local, gitignored):
    ./.polymath/project.local.yaml — deep-merged on top of the winning file
    (mappings merge per key with the overlay winning; lists and scalars are
    replaced). Overlay problems never fail the session: a malformed or
    invalid overlay is warned to stderr and skipped.

Outputs:
  ${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json — full snapshot
  the file plus a `_meta` block describing where the source file lives and
  when it was loaded (plus `overlay` when one applied and `ignored_keys`
  when unknown top-level keys were dropped). Skills consume this file to
  adapt behavior.

Validation:
  The script enforces a minimal subset of registry/schemas/project.schema.json:
  required top-level types, enum-bounded conventions, language list shape.
  Unknown top-level keys are warned and dropped (never fatal) so a config
  written for a newer schema degrades gracefully on an older loader.
  Surface-only validation; deep nested validation is the JSON schema's job
  for tooling that has a full validator (CI). The aim here is "block obvious
  typos that would corrupt the context snapshot" not full schema enforcement.

Exit codes:
  0 — success (with or without a project file)
  2 — project file present but invalid (overlay-only problems never exit 2)

Quiet by default. Verbose with POLYMATH_PROJECT_DEBUG=1.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import datetime
from typing import Any

DEBUG = os.environ.get("POLYMATH_PROJECT_DEBUG") == "1"


def _debug(msg: str) -> None:
    if DEBUG:
        print(f"polymath-core: {msg}", file=sys.stderr)


def _project_candidates() -> list[pathlib.Path]:
    out = [pathlib.Path.cwd() / ".polymath" / "project.yaml"]
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg:
        out.append(pathlib.Path(cfg) / "polymath" / "project.yaml")
    out.append(pathlib.Path.home() / ".polymath" / "project.yaml")
    return out


def _overlay_candidate() -> pathlib.Path:
    return pathlib.Path.cwd() / ".polymath" / "project.local.yaml"


def _data_root() -> pathlib.Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        return pathlib.Path(base) / "polymath-core"
    return pathlib.Path.home() / ".claude" / "plugins" / "data" / "polymath-core"


# ---------------------------------------------------------------------------
# YAML loader — same shim as polymath-flow's, but trimmed for the project
# subset (no block scalars; no inline-mapping-in-list-item beyond two levels).
# ---------------------------------------------------------------------------

try:
    import yaml  # type: ignore

    def _load_yaml(text: str) -> Any:
        return yaml.safe_load(text)
except ImportError:
    import re

    def _scalar(token: str) -> Any:
        token = token.strip()
        if not token:
            return None
        if (token.startswith('"') and token.endswith('"')) or (
            token.startswith("'") and token.endswith("'")
        ):
            return token[1:-1]
        if token.startswith("[") and token.endswith("]"):
            inner = token[1:-1].strip()
            if not inner:
                return []
            return [_scalar(p) for p in inner.split(",")]
        low = token.lower()
        if low in {"true", "yes"}:
            return True
        if low in {"false", "no"}:
            return False
        if low in {"null", "~", ""}:
            return None
        try:
            return int(token)
        except ValueError:
            pass
        try:
            return float(token)
        except ValueError:
            pass
        return token

    def _indent_of(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def _load_yaml(text: str) -> Any:  # noqa: C901
        lines: list[tuple[int, str]] = []
        for raw in text.splitlines():
            stripped = raw.rstrip()
            if not stripped.strip() or stripped.lstrip().startswith("#"):
                continue
            out = []
            in_q: str | None = None
            for ch in stripped:
                if in_q:
                    out.append(ch)
                    if ch == in_q:
                        in_q = None
                else:
                    if ch in ("'", '"'):
                        in_q = ch
                        out.append(ch)
                    elif ch == "#":
                        break
                    else:
                        out.append(ch)
            cleaned = "".join(out).rstrip()
            if cleaned.strip():
                lines.append((_indent_of(cleaned), cleaned.lstrip()))

        pos = 0

        def parse_block(indent: int) -> Any:
            nonlocal pos
            if pos >= len(lines):
                return None
            first_indent, first_line = lines[pos]
            if first_indent < indent:
                return None
            if first_line.startswith("- "):
                items: list[Any] = []
                while pos < len(lines):
                    cur_indent, cur_line = lines[pos]
                    if cur_indent < indent or not cur_line.startswith("- "):
                        break
                    body = cur_line[2:]
                    if ":" in body and not body.startswith("{"):
                        key, _, val = body.partition(":")
                        key = key.strip()
                        val = val.strip()
                        item: dict = {}
                        if val:
                            item[key] = _scalar(val)
                        else:
                            item[key] = None
                        pos += 1
                        sub_indent = indent + 2
                        while pos < len(lines):
                            ni, nl = lines[pos]
                            if ni < sub_indent:
                                break
                            if ni == sub_indent and ":" in nl and not nl.startswith("- "):
                                k, _, v = nl.partition(":")
                                k = k.strip()
                                v = v.strip()
                                if v == "":
                                    pos += 1
                                    item[k] = parse_block(sub_indent + 2)
                                else:
                                    item[k] = _scalar(v)
                                    pos += 1
                            elif ni == sub_indent and nl.startswith("- "):
                                break
                            else:
                                last_key = list(item.keys())[-1]
                                if item[last_key] is None:
                                    item[last_key] = parse_block(ni)
                                else:
                                    break
                        items.append(item)
                    else:
                        items.append(_scalar(body))
                        pos += 1
                return items
            result: dict = {}
            while pos < len(lines):
                cur_indent, cur_line = lines[pos]
                if cur_indent < indent or cur_indent > indent or cur_line.startswith("- "):
                    break
                if ":" not in cur_line:
                    break
                key, _, val = cur_line.partition(":")
                key = key.strip()
                val = val.strip()
                if val == "":
                    pos += 1
                    result[key] = parse_block(indent + 2)
                else:
                    result[key] = _scalar(val)
                    pos += 1
            return result

        return parse_block(0)


# ---------------------------------------------------------------------------
# Validation (minimal subset of registry/schemas/project.schema.json)
# ---------------------------------------------------------------------------

# Kept in sync with registry/schemas/project.schema.json `properties` — the
# pair is drift-guarded by a unit test in tests/test_project_context.py.
KNOWN_TOP_KEYS = {
    "schemaVersion",
    "project",
    "stack",
    "conventions",
    "external_skills",
    "capabilities",
    "setup",
    "polymath",
    "skill_overrides",
    "prompts",
    "conventions_docs",
    "smoke",
    "tracker",
    "routing",
    "attribution",
    "artifact_matrix",
}
COMMIT_STYLES = {"conventional-commits", "free-form", "ticket-prefixed"}
BRANCH_STRATEGIES = {"trunk-based", "gitflow", "github-flow", "release-branch"}
INSTALL_KINDS = {"marketplace", "manual", "submodule"}
ROUTING_MODES = {"hint", "classify", "enforce"}


def _split_unknown(data: dict) -> tuple[dict, list[str]]:
    """Drop top-level keys outside the known schema, returning (clean, dropped).

    Unknown keys warn instead of failing so a project file written for a
    newer schema (or carrying a typo) degrades gracefully on this loader.
    """
    unknown = sorted(set(data.keys()) - KNOWN_TOP_KEYS)
    if not unknown:
        return data, []
    return {k: v for k, v in data.items() if k in KNOWN_TOP_KEYS}, unknown


def _deep_merge(base: Any, overlay: Any) -> Any:
    """Merge overlay into base: mappings merge per key (overlay wins),
    lists and scalars are replaced by the overlay value."""
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    return overlay


def _validate(data: Any) -> list[str]:
    errs: list[str] = []
    if not isinstance(data, dict):
        return ["project.yaml root must be a mapping"]
    sv = data.get("schemaVersion")
    if sv != 1:
        errs.append(f"schemaVersion must be 1 (got {sv!r})")
    stack = data.get("stack")
    if stack is not None:
        if not isinstance(stack, dict):
            errs.append("stack must be a mapping")
        else:
            langs = stack.get("languages")
            if langs is not None:
                if not isinstance(langs, list) or not langs:
                    errs.append("stack.languages must be a non-empty list")
                else:
                    for i, l in enumerate(langs):
                        if not isinstance(l, dict) or "lang" not in l:
                            errs.append(f"stack.languages[{i}] missing `lang`")
    conv = data.get("conventions")
    if conv is not None:
        if not isinstance(conv, dict):
            errs.append("conventions must be a mapping")
        else:
            cs = conv.get("commit_style")
            if cs is not None and cs not in COMMIT_STYLES:
                errs.append(
                    f"conventions.commit_style {cs!r} not in {sorted(COMMIT_STYLES)}"
                )
            bs = conv.get("branch_strategy")
            if bs is not None and bs not in BRANCH_STRATEGIES:
                errs.append(
                    f"conventions.branch_strategy {bs!r} not in {sorted(BRANCH_STRATEGIES)}"
                )
    ext = data.get("external_skills")
    if ext is not None:
        if not isinstance(ext, list):
            errs.append("external_skills must be a list")
        else:
            for i, e in enumerate(ext):
                if not isinstance(e, dict) or "source" not in e:
                    errs.append(f"external_skills[{i}] missing `source`")
                    continue
                kind = e.get("install")
                if kind is not None and kind not in INSTALL_KINDS:
                    errs.append(
                        f"external_skills[{i}].install {kind!r} not in {sorted(INSTALL_KINDS)}"
                    )
    setup = data.get("setup")
    if setup is not None:
        if not isinstance(setup, dict):
            errs.append("setup must be a mapping")
        else:
            for key in ("context_sources", "required_tools", "environment", "first_steps"):
                value = setup.get(key)
                if value is not None and not isinstance(value, list):
                    errs.append(f"setup.{key} must be a list")
            for i, tool in enumerate(setup.get("required_tools") or []):
                if not isinstance(tool, dict) or not tool.get("name"):
                    errs.append(f"setup.required_tools[{i}] missing `name`")
            for i, var in enumerate(setup.get("environment") or []):
                if not isinstance(var, dict) or not var.get("name"):
                    errs.append(f"setup.environment[{i}] missing `name`")
    poly = data.get("polymath")
    if poly is not None:
        if not isinstance(poly, dict):
            errs.append("polymath must be a mapping")
        else:
            for key in ("recommended_plugins", "recommended_workflows", "compatible_agents"):
                value = poly.get(key)
                if value is not None and not isinstance(value, list):
                    errs.append(f"polymath.{key} must be a list")
            for i, plugin in enumerate(poly.get("recommended_plugins") or []):
                if not isinstance(plugin, dict) or not plugin.get("name"):
                    errs.append(f"polymath.recommended_plugins[{i}] missing `name`")
    for key in ("conventions_docs", "smoke", "tracker", "routing", "attribution"):
        value = data.get(key)
        if value is not None and not isinstance(value, dict):
            errs.append(f"{key} must be a mapping")
    am = data.get("artifact_matrix")
    if am is not None and not isinstance(am, str):
        errs.append("artifact_matrix must be a string path")
    routing = data.get("routing")
    if isinstance(routing, dict):
        mode = routing.get("mode")
        if mode is not None and mode not in ROUTING_MODES:
            errs.append(f"routing.mode {mode!r} not in {sorted(ROUTING_MODES)}")
    smoke = data.get("smoke")
    if isinstance(smoke, dict):
        for lang, recipe in smoke.items():
            if not isinstance(recipe, dict) or not recipe.get("start"):
                errs.append(f"smoke.{lang} missing `start`")
    return errs


# ---------------------------------------------------------------------------
# Summary line for SessionStart surfacing
# ---------------------------------------------------------------------------


def _summary_line(ctx: dict) -> str:
    stack = ctx.get("stack") or {}
    languages = stack.get("languages") or []
    lang_parts: list[str] = []
    for l in languages:
        if not isinstance(l, dict):
            continue
        token = l.get("lang", "?")
        ver = l.get("version")
        if ver:
            token = f"{token} {ver}"
        fw = l.get("framework")
        if fw:
            token = f"{token} ({fw})"
        lang_parts.append(token)
    testing = stack.get("testing") or []
    test_part = ""
    if testing and isinstance(testing[0], dict):
        t = testing[0]
        bits = [b for b in (t.get("framework"), t.get("mocking"), t.get("assertion")) if b]
        if bits:
            test_part = " + ".join(bits)
    ext = ctx.get("external_skills") or []
    runtime = (stack.get("runtime") or {}).get("kind")
    setup = ctx.get("setup") or {}
    tools = setup.get("required_tools") or []
    env_vars = setup.get("environment") or []
    poly = ctx.get("polymath") or {}
    recommended_plugins = poly.get("recommended_plugins") or []

    parts: list[str] = []
    if lang_parts:
        parts.append("Languages: " + ", ".join(lang_parts))
    if test_part:
        parts.append(f"Tests: {test_part}")
    if runtime:
        parts.append(f"Runtime: {runtime}")
    if ext:
        sources = [e.get("source") for e in ext if isinstance(e, dict) and e.get("source")]
        if sources:
            parts.append(f"External skills: {', '.join(sources)}")
    if tools or env_vars:
        setup_bits: list[str] = []
        if tools:
            setup_bits.append(f"{len(tools)} tool(s)")
        if env_vars:
            setup_bits.append(f"{len(env_vars)} env var(s)")
        parts.append("Setup: " + ", ".join(setup_bits))
    plugin_names = [
        p.get("name")
        for p in recommended_plugins
        if isinstance(p, dict) and p.get("name")
    ]
    if plugin_names:
        visible = plugin_names[:5]
        suffix = "" if len(plugin_names) <= 5 else f" +{len(plugin_names) - 5} more"
        parts.append(f"Recommended plugins: {', '.join(visible)}{suffix}")
    if not parts:
        return ""
    return "Polymath: project context loaded. " + " · ".join(parts)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def _read_overlay(path: pathlib.Path) -> dict | None:
    """Parse the machine-local overlay. Fail-open: any problem warns and
    returns None — a personal overlay must never break the session."""
    try:
        parsed = _load_yaml(path.read_text())
    except Exception as e:  # OSError or YAML error alike
        print(
            f"polymath-core: ignoring overlay {path}: {e}",
            file=sys.stderr,
        )
        return None
    if not isinstance(parsed, dict):
        print(
            f"polymath-core: ignoring overlay {path}: root must be a mapping",
            file=sys.stderr,
        )
        return None
    return parsed


def main() -> int:
    source: pathlib.Path | None = None
    for cand in _project_candidates():
        if cand.exists():
            source = cand
            break

    overlay_path = _overlay_candidate()
    overlay: dict | None = None
    if overlay_path.exists():
        overlay = _read_overlay(overlay_path)

    out_dir = _data_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "project-context.json"

    if source is None and overlay is None:
        # Clear any stale snapshot so downstream skills don't act on it.
        if out_file.exists():
            out_file.unlink()
        _debug("no .polymath/project.yaml found; cleared snapshot")
        return 0

    data: dict = {}
    if source is not None:
        try:
            text = source.read_text()
        except OSError as e:
            print(
                f"polymath-core: could not read project file {source}: {e}",
                file=sys.stderr,
            )
            return 2

        try:
            data = _load_yaml(text)
        except Exception as e:
            print(
                f"polymath-core: project file {source} is not valid YAML: {e}",
                file=sys.stderr,
            )
            return 2

        errs = _validate(data)
        if errs:
            print(
                f"polymath-core: project file {source} has {len(errs)} validation error(s):",
                file=sys.stderr,
            )
            for e in errs:
                print(f"  ✗ {e}", file=sys.stderr)
            return 2

    applied_overlay: pathlib.Path | None = None
    if overlay is not None:
        merged = _deep_merge(data, overlay) if source is not None else overlay
        merge_errs = _validate(merged)
        if merge_errs:
            # Fail-open: a bad overlay is skipped, never fatal.
            print(
                f"polymath-core: ignoring overlay {overlay_path} "
                f"({len(merge_errs)} validation error(s) after merge):",
                file=sys.stderr,
            )
            for e in merge_errs:
                print(f"  ✗ {e}", file=sys.stderr)
        else:
            data = merged
            applied_overlay = overlay_path

    if source is None and applied_overlay is None:
        # Overlay was the only candidate and it was skipped.
        if out_file.exists():
            out_file.unlink()
        _debug("only an invalid overlay found; cleared snapshot")
        return 0

    data, ignored_keys = _split_unknown(data)
    if ignored_keys:
        print(
            "polymath-core: ignoring unknown top-level key(s): "
            + ", ".join(ignored_keys)
            + " (not in the project schema — update polymath-core or fix typos)",
            file=sys.stderr,
        )

    snapshot = dict(data)
    meta = {
        "source": str(source if source is not None else overlay_path),
        "loaded_at": datetime.datetime.now(datetime.timezone.utc)
        .replace(tzinfo=None)
        .isoformat(timespec="seconds")
        + "Z",
        "schemaVersion": data.get("schemaVersion", 1),
    }
    if applied_overlay is not None and source is not None:
        meta["overlay"] = str(applied_overlay)
    if ignored_keys:
        meta["ignored_keys"] = ignored_keys
    snapshot["_meta"] = meta
    out_file.write_text(json.dumps(snapshot, indent=2))

    summary = _summary_line(snapshot)
    if summary:
        print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
