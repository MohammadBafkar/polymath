#!/usr/bin/env python3
"""Workflow-triggering tests.

Sibling of skill-triggering.py, for the workflow routing surface. A
workflow-triggering test asserts that a *naive* user prompt — one that does not
name the workflow — causes the model to PROPOSE the right workflow (per the
detect → propose → confirm → run contract in run-workflow/SKILL.md). It is the
falsification anchor for `whenToUse` / `triggers` quality: if those are generic,
the workflow won't surface, and this test catches it before real users do.

Test file shape: `tests/workflow-triggering/<workflow>.md`

```markdown
---
workflow: reviewPlan
trigger_prompts:
  - "review this plan"
  - "is this plan any good before I start"
  - "poke holes in this plan"
must_propose:
  - reviewPlan
allow_propose:
  - deliberationLoop        # acceptable runner-up on a tie
forbidden_prompts:
  - "format my markdown"     # must NOT propose any workflow
---
```

Run modes:
  check  — validate every test's frontmatter, that `workflow`/`must_propose`
           resolve to real workflow YAML, and that `trigger_prompts` are a
           superset-or-equal of the workflow's own `triggers` (drift guard).
           No LLM calls.
  list   — print one row per test file.
  run    — execute each prompt via `claude -p --output-format stream-json`
           (requires CLAUDE_CODE_OAUTH_TOKEN) and assert the model proposes the
           expected workflow. The model emits a one-line proposal as TEXT (it
           does not call a tool at propose time), so the assertion parses the
           assistant text for a backticked workflow name; it also accepts an
           explicit run-workflow / `polymath-flow start <name>` call as a match.

`run` is opt-in (real model calls). CI runs it in a gated job that is allowed to
be slow and is skipped on fork PRs.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests" / "workflow-triggering"
WORKFLOWS_DIR = ROOT / "plugins" / "polymath-flows" / "workflows"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _load_yaml(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text)
    # Minimal shim for our flat frontmatter / top-level-list shape.
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key is not None:
            result.setdefault(current_key, []).append(line[4:].strip().strip("\"'"))
            continue
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val == "":
                current_key = key
                result[key] = []
            else:
                current_key = None
                result[key] = val.strip("\"'")
    return result


def _workflow_index() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in sorted(WORKFLOWS_DIR.glob("*.yaml")):
        wf = _load_yaml(p.read_text()) or {}
        name = wf.get("name")
        if name:
            out[name] = wf
    return out


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
    out = []
    for p in sorted(TESTS_DIR.rglob("*.md")):
        if p.name == "README.md":
            continue
        out.append(_load_test(p))
    return out


def _validate(t: dict[str, Any], workflows: dict[str, dict]) -> list[str]:
    errs: list[str] = []
    wf_name = t.get("workflow")
    if not wf_name:
        errs.append("missing required field: workflow")
    elif wf_name not in workflows:
        errs.append(f"workflow {wf_name!r} has no matching YAML in {WORKFLOWS_DIR.name}/")
    prompts = t.get("trigger_prompts")
    if not isinstance(prompts, list) or len(prompts) < 3:
        errs.append("trigger_prompts must contain at least 3 prompts")
    must = t.get("must_propose")
    if not isinstance(must, list) or not must:
        errs.append("must_propose must list at least one workflow")
    else:
        for name in must:
            if name not in workflows:
                errs.append(f"must_propose entry {name!r} is not a known workflow")
    # Drift guard: every trigger declared on the workflow YAML must appear in the
    # test's trigger_prompts, so the test and the index can't silently diverge.
    if wf_name in workflows and isinstance(prompts, list):
        declared = set(workflows[wf_name].get("triggers") or [])
        missing = sorted(declared - set(prompts))
        if missing:
            errs.append(f"trigger_prompts missing YAML triggers: {missing}")
    return errs


def cmd_check() -> int:
    workflows = _workflow_index()
    tests = discover()
    if not tests:
        print(f"info: no workflow-triggering tests under {TESTS_DIR.relative_to(ROOT)}")
        return 0
    fail = 0
    for t in tests:
        errs = _validate(t, workflows)
        if errs:
            fail = 1
            for e in errs:
                print(f"::error file={t['_path']}::{e}")
        else:
            print(f"OK: {pathlib.Path(t['_path']).relative_to(ROOT)}")
    if fail:
        print("workflow-triggering check FAILED", file=sys.stderr)
    return fail


def cmd_list() -> int:
    tests = discover()
    print(f"{'WORKFLOW':26} {'PROMPTS':>7}  PATH")
    for t in tests:
        print(
            f"{t.get('workflow','?'):26} {len(t.get('trigger_prompts',[])):>7}  "
            f"{pathlib.Path(t['_path']).relative_to(ROOT)}"
        )
    return 0


# --- live run mode ---------------------------------------------------------

_WORKFLOW_NAMES = set()


def _extract_proposals(stream_json: str) -> list[str]:
    """Return workflow names the model proposed. Primary signal: a backticked
    name inside an assistant text sentence that mentions "workflow". Fallback:
    an explicit run-workflow Skill call or a `polymath-flow start <name>` Bash
    command (covers the "just run it" path)."""
    proposed: list[str] = []
    sentence_re = re.compile(r"[^.!?\n]*`([A-Za-z][A-Za-z0-9]*)`[^.!?\n]*", re.S)
    start_re = re.compile(r"polymath-flow\s+start\s+([A-Za-z][A-Za-z0-9]*)")
    for line in stream_json.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        nodes: list[Any] = [ev]
        msg = ev.get("message") if isinstance(ev, dict) else None
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            nodes.extend(msg["content"])
        for n in nodes:
            if not isinstance(n, dict):
                continue
            if n.get("type") == "text" and isinstance(n.get("text"), str):
                txt = n["text"]
                for seg in re.split(r"(?<=[.!?\n])", txt):
                    if "workflow" not in seg.lower():
                        continue
                    for m in re.finditer(r"`([A-Za-z][A-Za-z0-9]*)`", seg):
                        if m.group(1) in _WORKFLOW_NAMES:
                            proposed.append(m.group(1))
            if n.get("type") == "tool_use":
                inp = n.get("input") or {}
                if n.get("name") == "Skill" and isinstance(inp, dict):
                    arg = str(inp.get("args", ""))
                    for nm in _WORKFLOW_NAMES:
                        if re.search(rf"\b{re.escape(nm)}\b", arg):
                            proposed.append(nm)
                if n.get("name") == "Bash" and isinstance(inp, dict):
                    for m in start_re.finditer(str(inp.get("command", ""))):
                        if m.group(1) in _WORKFLOW_NAMES:
                            proposed.append(m.group(1))
    # de-dup, preserve order
    seen: set[str] = set()
    return [p for p in proposed if not (p in seen or seen.add(p))]


def _run_prompt(prompt: str, *, timeout: int) -> tuple[int, str]:
    if shutil.which("claude") is None:
        return -1, ""
    cmd = [
        "claude", "-p", "--permission-mode", "dontAsk",
        "--no-session-persistence", "--output-format", "stream-json", prompt,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or "") + (e.stderr or "")
    return proc.returncode, proc.stdout or ""


def cmd_run(timeout: int) -> int:
    if shutil.which("claude") is None:
        print(
            "workflow-triggering run: claude CLI not on PATH — skipping (expected "
            "for fork PRs without secrets; CI treats this as a skip, not a failure)."
        )
        return 0
    global _WORKFLOW_NAMES
    workflows = _workflow_index()
    _WORKFLOW_NAMES = set(workflows)
    tests = discover()
    if not tests:
        print("info: no workflow-triggering tests to run")
        return 0
    failures = 0
    for t in tests:
        errs = _validate(t, workflows)
        if errs:
            print(f"::error file={t['_path']}::test invalid; first error: {errs[0]}")
            failures += 1
            continue
        must = t.get("must_propose", [])
        allow = set(must) | set(t.get("allow_propose", []) or [])
        label = t["workflow"]
        for prompt in t.get("trigger_prompts", []):
            rc, out = _run_prompt(prompt, timeout=timeout)
            if rc == -1:
                print(f"::warning::{label}: claude CLI vanished mid-run")
                continue
            proposed = _extract_proposals(out)
            missing = [m for m in must if m not in proposed]
            forbidden = [p for p in proposed if p not in allow]
            if missing or forbidden:
                failures += 1
                print(
                    f"::error file={t['_path']}::{label}: prompt={prompt!r} "
                    f"proposed={proposed} missing={missing} forbidden={forbidden}"
                )
            else:
                print(f"OK: {label} ← {prompt!r} (proposed: {proposed})")
        for prompt in t.get("forbidden_prompts", []) or []:
            rc, out = _run_prompt(prompt, timeout=timeout)
            if rc == -1:
                continue
            proposed = _extract_proposals(out)
            if proposed:
                failures += 1
                print(
                    f"::error file={t['_path']}::{label}: forbidden prompt "
                    f"{prompt!r} proposed {proposed} (expected none)"
                )
            else:
                print(f"OK: {label} ✗ {prompt!r} (no proposal, correct)")
    if failures:
        print(f"workflow-triggering run FAILED ({failures} mismatch(es))", file=sys.stderr)
        return 1
    return 0


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
