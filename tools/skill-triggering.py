#!/usr/bin/env python3
"""Skill-triggering tests.

A skill-triggering test asserts that a *naive* user prompt — one that doesn't
mention the skill by name — causes the model to load the right Polymath skill.
This is the falsification anchor for skill `description:` quality. If the
description is generic, the skill won't trigger; the test catches that before
real users do.

Test file shape: `tests/skill-triggering/<plugin>/<skill>.md`

```markdown
---
plugin: polymath-product
skill: prd
trigger_prompts:
  - "draft a PRD for rate-limiting /login"
  - "we need a product spec for the new refund flow"
must_invoke:
  - polymath-product:prd
allow_invoke:
  - polymath-thinking:*
forbidden_prompts:
  - "format my markdown"        # should NOT trigger this skill
---
```

Run modes:

  check   — validate every test file's frontmatter (no LLM calls).
  list    — print one row per test file.
  run     — execute each prompt via `claude -p --output-format stream-json`
            (requires CLAUDE_CODE_OAUTH_TOKEN), inspect the resulting tool
            calls, assert the expected Skill invocation happens.

`run` is opt-in (it costs real model calls). CI invokes it under a separate
job that is allowed to be slow + skipped on fork PRs.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # parsed via inline shim below


ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests" / "skill-triggering"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


# ---------------------------------------------------------------------------
# YAML loader (PyYAML when available; inline shim otherwise)
# ---------------------------------------------------------------------------

def _load_yaml(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text)
    # Minimal shim — supports our flat frontmatter shape only.
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key is not None:
            val = line[4:].strip().strip("\"'")
            result.setdefault(current_key, []).append(val)
            continue
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                current_key = key
                result[key] = []
            else:
                current_key = None
                v = val.strip("\"'")
                result[key] = v
    return result


# ---------------------------------------------------------------------------
# Test discovery + validation
# ---------------------------------------------------------------------------


def _load_test(path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fm = _load_yaml(m.group(1))
    if not isinstance(fm, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")
    fm["_path"] = str(path)
    return fm


def discover() -> list[dict[str, Any]]:
    if not TESTS_DIR.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for p in sorted(TESTS_DIR.rglob("*.md")):
        if p.name == "README.md":
            continue
        out.append(_load_test(p))
    return out


def _validate(t: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for required in ("plugin", "skill", "trigger_prompts", "must_invoke"):
        if not t.get(required):
            errs.append(f"missing required field: {required}")
    if isinstance(t.get("plugin"), str) and not re.match(r"^[a-z0-9-]+$", t["plugin"]):
        errs.append(f"plugin {t['plugin']!r} must be kebab-case")
    if isinstance(t.get("skill"), str) and not re.match(r"^[a-z][a-z0-9-]*$", t["skill"]):
        errs.append(f"skill {t['skill']!r} must be kebab-case")
    prompts = t.get("trigger_prompts")
    if isinstance(prompts, list) and len(prompts) < 1:
        errs.append("trigger_prompts must contain at least one prompt")
    invoke = t.get("must_invoke")
    if isinstance(invoke, list):
        for entry in invoke:
            if not isinstance(entry, str) or ":" not in entry:
                errs.append(f"must_invoke entry {entry!r} must be 'plugin:skill'")
    return errs


def cmd_check() -> int:
    tests = discover()
    if not tests:
        print(f"info: no skill-triggering tests under {TESTS_DIR.relative_to(ROOT)}")
        return 0
    fail = 0
    for t in tests:
        errs = _validate(t)
        if errs:
            fail = 1
            for e in errs:
                print(f"::error file={t['_path']}::{e}")
        else:
            print(f"OK: {pathlib.Path(t['_path']).relative_to(ROOT)}")
    if fail:
        print(f"skill-triggering check FAILED ({fail} bad file(s))", file=sys.stderr)
    return fail


def cmd_list() -> int:
    tests = discover()
    print(f"{'PLUGIN':30} {'SKILL':30} {'PROMPTS':>8}  PATH")
    for t in tests:
        print(
            f"{t.get('plugin','?'):30} {t.get('skill','?'):30} "
            f"{len(t.get('trigger_prompts',[])):>8}  "
            f"{pathlib.Path(t['_path']).relative_to(ROOT)}"
        )
    return 0


# ---------------------------------------------------------------------------
# Live run mode (opt-in)
# ---------------------------------------------------------------------------


def _extract_skill_invocations(stream_json: str) -> list[str]:
    """Walk a `claude -p --output-format stream-json` transcript and return
    every `Skill` tool-use's resolved name. Each event line is a JSON object
    on its own line."""
    out: list[str] = []
    for line in stream_json.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Tool-use events come in different shapes depending on stream version;
        # check both top-level and message.content paths.
        nodes: list[Any] = [ev]
        msg = ev.get("message") if isinstance(ev, dict) else None
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            nodes.extend(msg["content"])
        for n in nodes:
            if not isinstance(n, dict):
                continue
            if n.get("type") == "tool_use" and n.get("name") == "Skill":
                inp = n.get("input") or {}
                skill = inp.get("skill") if isinstance(inp, dict) else None
                if isinstance(skill, str):
                    out.append(skill)
    return out


def _match_any(needle: str, patterns: Iterable[str]) -> bool:
    for p in patterns:
        if fnmatch.fnmatchcase(needle, p):
            return True
    return False


def _run_prompt(prompt: str, *, timeout: int) -> tuple[int, str]:
    """Run claude -p with stream-json output, return (returncode, stdout).
    Returns (-1, '') when claude is not on PATH so callers can skip."""
    if shutil.which("claude") is None:
        return -1, ""
    cmd = [
        "claude",
        "-p",
        "--permission-mode",
        "dontAsk",
        "--no-session-persistence",
        "--output-format",
        "stream-json",
        prompt,
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or "") + (e.stderr or "")
    return proc.returncode, proc.stdout or ""


def cmd_run(timeout: int) -> int:
    if shutil.which("claude") is None:
        print(
            "skill-triggering run: claude CLI not on PATH — skipping (this is "
            "expected for fork PRs without secrets; CI's gated run mode treats "
            "this as a skip, not a failure)."
        )
        return 0
    tests = discover()
    if not tests:
        print("info: no skill-triggering tests to run")
        return 0
    failures = 0
    for t in tests:
        errs = _validate(t)
        if errs:
            print(
                f"::error file={t['_path']}::test invalid; "
                f"first error: {errs[0]}"
            )
            failures += 1
            continue
        must = t.get("must_invoke", [])
        allow = list(must) + list(t.get("allow_invoke", []) or [])
        label = f"{t['plugin']}:{t['skill']}"
        for prompt in t.get("trigger_prompts", []):
            rc, out = _run_prompt(prompt, timeout=timeout)
            if rc == -1:
                # claude vanished between discovery and now (shouldn't happen)
                print(f"::warning::{label}: claude CLI vanished mid-run")
                continue
            invoked = _extract_skill_invocations(out)
            missing = [m for m in must if not any(fnmatch.fnmatchcase(i, m) for i in invoked)]
            forbidden = [
                i for i in invoked
                if not _match_any(i, allow)
            ]
            if missing or forbidden:
                failures += 1
                print(
                    f"::error file={t['_path']}::{label}: prompt={prompt!r} "
                    f"invoked={invoked} missing={missing} forbidden={forbidden}"
                )
            else:
                print(f"OK: {label} ← {prompt!r} (invoked: {invoked})")
    if failures:
        print(f"skill-triggering run FAILED ({failures} mismatch(es))", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("list")
    rp = sub.add_parser("run")
    rp.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "list":
        return cmd_list()
    if args.cmd == "run":
        return cmd_run(args.timeout)
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
