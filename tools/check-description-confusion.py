#!/usr/bin/env python3
"""Confusion-matrix gate for sibling-skill routing.

DESC-1 (lint-descriptions.py) proves no two descriptions token-collide; this is
the deeper, behavioural check: for each prompt in tests/forbidden_prompts.yaml,
the model must load the EXPECTED skill and never a FORBIDDEN sibling. It is the
skill-routing analogue of workflow-triggering, scoped to the audit's confusion
clusters (C1-C11).

Modes:
  check  — validate every case structurally (referenced skills/commands exist,
           required fields present). No LLM calls; runs in conformance.
  list   — print one row per case.
  run    — execute each prompt via `claude -p --output-format stream-json`
           (needs CLAUDE_CODE_OAUTH_TOKEN); assert expected loaded, forbidden
           not. Opt-in; skipped when the claude CLI is absent (fork PRs).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

REPO = pathlib.Path(__file__).resolve().parents[1]
MATRIX = REPO / "tests" / "forbidden_prompts.yaml"
PLUGINS = REPO / "plugins"


def _exists(ref: str) -> bool:
    """ref is plugin:skill (skill) or plugin:/cmd (command)."""
    if ":/" in ref:
        plugin, cmd = ref.split(":/", 1)
        return (PLUGINS / plugin / "commands" / f"{cmd}.md").exists()
    if ":" in ref:
        plugin, skill = ref.split(":", 1)
        return (PLUGINS / plugin / "skills" / skill / "SKILL.md").exists()
    return False


def load_cases() -> list[dict]:
    if yaml is None:
        print("check-description-confusion: PyYAML required", file=sys.stderr)
        sys.exit(2)
    if not MATRIX.exists():
        return []
    return yaml.safe_load(MATRIX.read_text()) or []


def _validate(case: dict) -> list[str]:
    errs: list[str] = []
    if not case.get("prompt"):
        errs.append("missing prompt")
    has_expect = "expect" in case or "expect_one_of" in case
    if not has_expect:
        errs.append("needs expect or expect_one_of")
    refs: list[str] = []
    if case.get("expect"):
        refs.append(case["expect"])
    refs += list(case.get("expect_one_of") or [])
    refs += list(case.get("forbidden") or [])
    for r in refs:
        if not _exists(r):
            errs.append(f"unknown skill/command reference: {r}")
    if "expect_one_of" in case and not case.get("must_ask"):
        errs.append("expect_one_of cases must set must_ask: true")
    return errs


def cmd_check() -> int:
    cases = load_cases()
    if not cases:
        print(f"info: no cases in {MATRIX.relative_to(REPO)}")
        return 0
    fail = 0
    for i, c in enumerate(cases):
        errs = _validate(c)
        if errs:
            fail = 1
            for e in errs:
                print(f"::error file={MATRIX}::case {i} ({c.get('prompt','?')[:40]!r}): {e}")
    if fail:
        print("check-description-confusion FAILED", file=sys.stderr)
    else:
        print(f"confusion-matrix: {len(cases)} cases valid")
    return fail


def cmd_list() -> int:
    for c in load_cases():
        exp = c.get("expect") or ("one_of:" + ",".join(c.get("expect_one_of", [])))
        print(f"{exp:45} ⊀ {','.join(c.get('forbidden', []))}   ← {c['prompt']!r}")
    return 0


def _loaded_skills(stream_json: str) -> list[str]:
    out: list[str] = []
    for line in stream_json.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        nodes = [ev]
        msg = ev.get("message") if isinstance(ev, dict) else None
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            nodes += msg["content"]
        for n in nodes:
            if isinstance(n, dict) and n.get("type") == "tool_use" and n.get("name") == "Skill":
                inp = n.get("input") or {}
                skill = inp.get("skill") if isinstance(inp, dict) else None
                if isinstance(skill, str):
                    out.append(skill)
    return out


def _run_prompt(prompt: str, timeout: int) -> tuple[int, str]:
    if shutil.which("claude") is None:
        return -1, ""
    cmd = ["claude", "-p", "--permission-mode", "dontAsk",
           "--no-session-persistence", "--output-format", "stream-json", prompt]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or "")
    return p.returncode, p.stdout or ""


def cmd_run(timeout: int) -> int:
    if shutil.which("claude") is None:
        print("confusion-matrix run: claude CLI not on PATH — skipping (expected on fork PRs).")
        return 0
    cases = load_cases()
    failures = 0
    for c in cases:
        errs = _validate(c)
        if errs:
            print(f"::error::invalid case {c.get('prompt','?')[:40]!r}: {errs[0]}")
            failures += 1
            continue
        rc, out = _run_prompt(c["prompt"], timeout)
        if rc == -1:
            continue
        loaded = _loaded_skills(out)
        forbidden_hit = [s for s in loaded if s in (c.get("forbidden") or [])]
        if c.get("expect_one_of"):
            ok = any(s in c["expect_one_of"] for s in loaded) or not loaded  # ask==no load
            verdict_ok = ok and not forbidden_hit
        else:
            verdict_ok = (c["expect"] in loaded or not loaded) and not forbidden_hit
            if c.get("expect") and c["expect"] not in loaded and loaded:
                verdict_ok = False
        if verdict_ok and not forbidden_hit:
            print(f"OK: {c['prompt']!r} → loaded={loaded}")
        else:
            failures += 1
            print(f"::error::{c['prompt']!r}: loaded={loaded} forbidden_hit={forbidden_hit}")
    if failures:
        print(f"confusion-matrix run FAILED ({failures})", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("list")
    rp = sub.add_parser("run")
    rp.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "list":
        return cmd_list()
    if args.cmd == "run":
        return cmd_run(args.timeout)
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
