#!/usr/bin/env python3
"""Triggering tests and held-out routing eval — one subcommand per routing surface.

  triggering.py skill check|list|run [--timeout N] [--allow-empty]
  triggering.py workflow check|list|run [--timeout N] [--allow-empty]
  triggering.py route [check|list|run] [--allow-empty]
  triggering.py route-eval [--json]

skill — a skill-triggering test asserts that a *naive* user prompt (one that
doesn't mention the skill by name) causes the model to load the right Polymath
skill. This is the falsification anchor for skill `description:` quality: if
the description is generic, the skill won't trigger, and the test catches that
before real users do. Test file shape
(`tests/skill-triggering/<plugin>/<skill>.md`):

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

workflow — the same idea for the workflow routing surface: a naive prompt must
make the model PROPOSE the right workflow (per the detect → propose → confirm →
run contract in run-workflow/SKILL.md). `check` additionally verifies that
`workflow`/`must_propose` resolve to real workflow YAML and that
`trigger_prompts` are a superset-or-equal of the workflow's own `triggers`
(drift guard). Test file shape (`tests/workflow-triggering/<workflow>.md`):

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
      - "format my markdown"    # must NOT propose any workflow
    ---

route — asserts that the *deterministic* ambient routing hook
(`plugins/polymath-core/hooks/scripts/route-hint.py`) proposes the right
surface for a given prompt — or correctly stays silent. Unlike skill/workflow,
this harness needs **no model and no token**: the hook's output is a pure
function of the prompt text and the bundled signal table, so `route run`
executes in CI on every PR (the ROUTE-TRIGGER gate) and makes routing
precision a gateable metric. Fixture shape (`tests/route-triggering/<id>.md`):

    ---
    prompt: "Review this PR https://github.com/acme/web/pull/42 for correctness."
    must_appear:
      - "polymath-flows:run-workflow reviewPR"
    must_not_appear:        # optional
      - "respondToIncident"
    ---

Negative fixtures set `expect_silent: true` instead of `must_appear`. An
optional `overlay` key (a single-line JSON string, so the no-PyYAML shim can
parse the frontmatter) is written verbatim to
`.polymath/route-signals.project.json` inside the fixture's scratch cwd before
the hook runs — fixtures may carry junk on purpose to assert the hook degrades
quiet on a malformed overlay. Every `route run` executes the hook hermetically:
a fresh scratch cwd with a `.git` sentinel and POLYMATH_ROUTE_MUTE scrubbed
from the environment, so neither this repo's own `.polymath/` nor
developer-machine state can flip the gate.

route-eval — held-out routing MEASUREMENT (Claim A: does the deterministic
router fire correctly?). This is NOT tests/route-triggering/*.md; those
fixtures are green by construction (authored to pass, wired into conformance
as a gate). This is a HELD-OUT eval: naturalistic prompts written the way a
user actually phrases a task, NOT reverse-engineered from the signal table,
plus deliberately-signalled prompts to measure precision and adversarial
negatives to measure false positives. It is a MEASUREMENT, not a gate: it
always exits 0 and is not wired into conformance. Its only job is to produce
honest numbers about the route-hint hook — including misses. Categories
(tests/route-eval/heldout.jsonl):

  naturalistic  Plain-English task. Measures REACH: how often the hard-signal
                router fires at all on natural phrasing. Non-firing is BY
                DESIGN (the router requires a hard signal), so it is reported,
                not failed.
  token         A hard signal (url / cve / path+intent) is deliberately
                present. Measures PRECISION: fire AND route to the right
                surface.
  negative      Should stay silent. Measures the FALSE-POSITIVE rate.
  ambiguous     Two surfaces compete. Reports the top candidate and whether
                the expected surface appears; the observation is the result.

The `skill run` and `workflow run` modes execute each prompt via
`claude -p --output-format stream-json` (requires CLAUDE_CODE_OAUTH_TOKEN),
inspect the transcript, and assert the expectation. They are opt-in (real
model calls); CI runs them in a gated job that is allowed to be slow and is
skipped on fork PRs. At propose time the model emits a one-line proposal as
TEXT (it does not call a tool), so the workflow assertion parses assistant
text for a backticked workflow name and also accepts an explicit run-workflow
/ `polymath-flow start <name>` call as a match.
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
import tempfile
from typing import Any, Iterable

from lib.frontmatter import FRONTMATTER_RE
from lib.repo import repo_root
from lib.yamlshim import load_yaml

ROOT = repo_root()
HOOK = ROOT / "plugins" / "polymath-core" / "hooks" / "scripts" / "route-hint.py"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _no_fixtures(label: str, what: str, allow_empty: bool) -> int:
    """A gate with zero fixtures is a silent no-op, not a pass. Fail by
    default so a deleted/moved fixture set can't make this gate green."""
    if allow_empty:
        print(f"{label}: {what} — allowed by --allow-empty")
        return 0
    print(
        f"{label}: {what} — refusing to pass an empty gate "
        f"(pass --allow-empty to override)",
        file=sys.stderr,
    )
    return 1


def _run_claude_prompt(prompt: str, *, timeout: int) -> tuple[int, str]:
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


# ---------------------------------------------------------------------------
# skill — naive prompt must load the right skill
# ---------------------------------------------------------------------------

SKILL_TESTS_DIR = ROOT / "tests" / "skill-triggering"


def _skill_load_test(path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fm = load_yaml(m.group(1))
    if not isinstance(fm, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")
    fm["_path"] = str(path)
    return fm


def skill_discover() -> list[dict[str, Any]]:
    if not SKILL_TESTS_DIR.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for p in sorted(SKILL_TESTS_DIR.rglob("*.md")):
        if p.name == "README.md":
            continue
        out.append(_skill_load_test(p))
    return out


def _skill_validate(t: dict[str, Any]) -> list[str]:
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


def skill_check(allow_empty: bool = False) -> int:
    tests = skill_discover()
    if not tests:
        return _no_fixtures(
            "skill-triggering check",
            f"no tests under {SKILL_TESTS_DIR.relative_to(ROOT)}",
            allow_empty,
        )
    fail = 0
    for t in tests:
        errs = _skill_validate(t)
        if errs:
            fail = 1
            for e in errs:
                print(f"::error file={t['_path']}::{e}")
        else:
            print(f"OK: {pathlib.Path(t['_path']).relative_to(ROOT)}")
    if fail:
        print(f"skill-triggering check FAILED ({fail} bad file(s))", file=sys.stderr)
    return fail


def skill_list() -> int:
    tests = skill_discover()
    print(f"{'PLUGIN':30} {'SKILL':30} {'PROMPTS':>8}  PATH")
    for t in tests:
        print(
            f"{t.get('plugin','?'):30} {t.get('skill','?'):30} "
            f"{len(t.get('trigger_prompts',[])):>8}  "
            f"{pathlib.Path(t['_path']).relative_to(ROOT)}"
        )
    return 0


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


def skill_run(timeout: int, allow_empty: bool = False) -> int:
    if shutil.which("claude") is None:
        print(
            "skill-triggering run: claude CLI not on PATH — skipping (this is "
            "expected for fork PRs without secrets; CI's gated run mode treats "
            "this as a skip, not a failure)."
        )
        return 0
    tests = skill_discover()
    if not tests:
        return _no_fixtures(
            "skill-triggering run",
            f"no tests under {SKILL_TESTS_DIR.relative_to(ROOT)}",
            allow_empty,
        )
    failures = 0
    for t in tests:
        errs = _skill_validate(t)
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
            rc, out = _run_claude_prompt(prompt, timeout=timeout)
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
# workflow — naive prompt must make the model propose the right workflow
# ---------------------------------------------------------------------------

WF_TESTS_DIR = ROOT / "tests" / "workflow-triggering"
WORKFLOWS_DIR = ROOT / "plugins" / "polymath-flows" / "workflows"


def _workflow_index() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in sorted(WORKFLOWS_DIR.glob("*.yaml")):
        wf = load_yaml(p.read_text()) or {}
        name = wf.get("name")
        if name:
            out[name] = wf
    return out


def _wf_load_test(path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fm = load_yaml(m.group(1))
    if not isinstance(fm, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")
    fm["_path"] = str(path)
    return fm


def wf_discover() -> list[dict[str, Any]]:
    if not WF_TESTS_DIR.is_dir():
        return []
    out = []
    for p in sorted(WF_TESTS_DIR.rglob("*.md")):
        if p.name == "README.md":
            continue
        out.append(_wf_load_test(p))
    return out


def _wf_validate(t: dict[str, Any], workflows: dict[str, dict]) -> list[str]:
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


def wf_check(allow_empty: bool = False) -> int:
    workflows = _workflow_index()
    tests = wf_discover()
    if not tests:
        return _no_fixtures(
            "workflow-triggering check",
            f"no tests under {WF_TESTS_DIR.relative_to(ROOT)}",
            allow_empty,
        )
    fail = 0
    for t in tests:
        errs = _wf_validate(t, workflows)
        if errs:
            fail = 1
            for e in errs:
                print(f"::error file={t['_path']}::{e}")
        else:
            print(f"OK: {pathlib.Path(t['_path']).relative_to(ROOT)}")
    if fail:
        print("workflow-triggering check FAILED", file=sys.stderr)
    return fail


def wf_list() -> int:
    tests = wf_discover()
    print(f"{'WORKFLOW':26} {'PROMPTS':>7}  PATH")
    for t in tests:
        print(
            f"{t.get('workflow','?'):26} {len(t.get('trigger_prompts',[])):>7}  "
            f"{pathlib.Path(t['_path']).relative_to(ROOT)}"
        )
    return 0


def _extract_proposals(stream_json: str, workflow_names: set[str]) -> list[str]:
    """Return workflow names the model proposed. Primary signal: a backticked
    name inside an assistant text sentence that mentions "workflow". Fallback:
    an explicit run-workflow Skill call or a `polymath-flow start <name>` Bash
    command (covers the "just run it" path)."""
    proposed: list[str] = []
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
                        if m.group(1) in workflow_names:
                            proposed.append(m.group(1))
            if n.get("type") == "tool_use":
                inp = n.get("input") or {}
                if n.get("name") == "Skill" and isinstance(inp, dict):
                    arg = str(inp.get("args", ""))
                    for nm in workflow_names:
                        if re.search(rf"\b{re.escape(nm)}\b", arg):
                            proposed.append(nm)
                if n.get("name") == "Bash" and isinstance(inp, dict):
                    for m in start_re.finditer(str(inp.get("command", ""))):
                        if m.group(1) in workflow_names:
                            proposed.append(m.group(1))
    # de-dup, preserve order
    seen: set[str] = set()
    return [p for p in proposed if not (p in seen or seen.add(p))]


def wf_run(timeout: int, allow_empty: bool = False) -> int:
    if shutil.which("claude") is None:
        print(
            "workflow-triggering run: claude CLI not on PATH — skipping (expected "
            "for fork PRs without secrets; CI treats this as a skip, not a failure)."
        )
        return 0
    workflows = _workflow_index()
    workflow_names = set(workflows)
    tests = wf_discover()
    if not tests:
        return _no_fixtures(
            "workflow-triggering run",
            f"no tests under {WF_TESTS_DIR.relative_to(ROOT)}",
            allow_empty,
        )
    failures = 0
    for t in tests:
        errs = _wf_validate(t, workflows)
        if errs:
            print(f"::error file={t['_path']}::test invalid; first error: {errs[0]}")
            failures += 1
            continue
        must = t.get("must_propose", [])
        allow = set(must) | set(t.get("allow_propose", []) or [])
        label = t["workflow"]
        for prompt in t.get("trigger_prompts", []):
            rc, out = _run_claude_prompt(prompt, timeout=timeout)
            if rc == -1:
                print(f"::warning::{label}: claude CLI vanished mid-run")
                continue
            proposed = _extract_proposals(out, workflow_names)
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
            rc, out = _run_claude_prompt(prompt, timeout=timeout)
            if rc == -1:
                continue
            proposed = _extract_proposals(out, workflow_names)
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


# ---------------------------------------------------------------------------
# route — deterministic route-hint hook fixtures (the ROUTE-TRIGGER gate)
# ---------------------------------------------------------------------------

ROUTE_TESTS_DIR = ROOT / "tests" / "route-triggering"


def _route_parse_fixture(path: pathlib.Path) -> dict:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path.name}: missing YAML frontmatter")
    fm = load_yaml(m.group(1)) or {}
    if not isinstance(fm, dict):
        raise ValueError(f"{path.name}: frontmatter is not a mapping")
    if not fm.get("prompt"):
        raise ValueError(f"{path.name}: missing required `prompt`")
    silent = bool(fm.get("expect_silent"))
    must = fm.get("must_appear") or []
    if isinstance(must, str):
        must = [must]
    if not silent and not must:
        raise ValueError(f"{path.name}: needs `must_appear` or `expect_silent: true`")
    if silent and must:
        raise ValueError(f"{path.name}: `expect_silent` and `must_appear` are mutually exclusive")
    not_must = fm.get("must_not_appear") or []
    if isinstance(not_must, str):
        not_must = [not_must]
    overlay = fm.get("overlay")
    if overlay is not None and not isinstance(overlay, str):
        raise ValueError(f"{path.name}: `overlay` must be a single-line JSON string")
    return {
        "id": path.stem,
        "prompt": fm["prompt"],
        "expect_silent": silent,
        "must_appear": must,
        "must_not_appear": not_must,
        "overlay": overlay,
    }


def _route_fixtures() -> list[pathlib.Path]:
    if not ROUTE_TESTS_DIR.is_dir():
        return []
    return sorted(ROUTE_TESTS_DIR.glob("*.md"))


def _route_run_hook(prompt: str, overlay: str | None = None) -> str:
    """Run the hook hermetically: a fresh scratch cwd (so this repo's own
    .polymath/ and any developer overlay can't leak into the gate) and a
    scrubbed environment. `overlay` is written verbatim to the scratch
    .polymath/route-signals.project.json — including deliberately broken
    content, to assert the hook degrades quiet."""
    payload = json.dumps({"prompt": prompt})
    env = {k: v for k, v in os.environ.items() if k != "POLYMATH_ROUTE_MUTE"}
    with tempfile.TemporaryDirectory(prefix="route-trigger-") as scratch:
        # .git sentinel: the hook's mute/overlay walks stop at a repo root,
        # so without one they would escape the scratch dir and could pick up
        # developer-machine state (e.g. a TMPDIR under $HOME).
        (pathlib.Path(scratch) / ".git").mkdir()
        if overlay is not None:
            overlay_dir = pathlib.Path(scratch) / ".polymath"
            overlay_dir.mkdir()
            (overlay_dir / "route-signals.project.json").write_text(overlay)
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=scratch,
            env=env,
        )
    return proc.stdout


def route_check(allow_empty: bool = False) -> int:
    files = _route_fixtures()
    if not files:
        return _no_fixtures(
            "route-triggering check",
            "no fixtures found (tests/route-triggering/*.md)",
            allow_empty,
        )
    errs = []
    for f in files:
        try:
            _route_parse_fixture(f)
        except Exception as e:  # noqa: BLE001
            errs.append(str(e))
    for e in errs:
        print(f"  FAIL  {e}")
    print(f"route-triggering check: {len(files)} fixture(s), {len(errs)} error(s)")
    return 1 if errs else 0


def route_list() -> int:
    for f in _route_fixtures():
        try:
            fx = _route_parse_fixture(f)
        except Exception as e:  # noqa: BLE001
            print(f"  (invalid) {f.name}: {e}")
            continue
        kind = "silent" if fx["expect_silent"] else "expect"
        target = "—" if fx["expect_silent"] else ", ".join(fx["must_appear"])
        print(f"  {fx['id']:<28} {kind:<7} {target}")
    return 0


def route_run(allow_empty: bool = False) -> int:
    if not HOOK.exists():
        print(f"route-triggering run: hook not found at {HOOK}", file=sys.stderr)
        return 1
    files = _route_fixtures()
    if not files:
        return _no_fixtures(
            "route-triggering run",
            "no fixtures found (tests/route-triggering/*.md)",
            allow_empty,
        )
    passed = failed = 0
    for f in files:
        try:
            fx = _route_parse_fixture(f)
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  {f.name}: {e}")
            failed += 1
            continue
        out = _route_run_hook(fx["prompt"], fx.get("overlay"))
        problems = []
        if fx["expect_silent"]:
            if out.strip():
                problems.append(f"expected silence, got:\n{_indent(out)}")
        else:
            for needle in fx["must_appear"]:
                if needle not in out:
                    problems.append(f"missing {needle!r}")
            for needle in fx["must_not_appear"]:
                if needle in out:
                    problems.append(f"unexpected {needle!r}")
        if problems:
            failed += 1
            print(f"  FAIL  {fx['id']}")
            for p in problems:
                print(f"          {p}")
        else:
            passed += 1
            print(f"  ok    {fx['id']}")
    print(f"route-triggering run: {passed} passed, {failed} failed")
    return 1 if failed else 0


def _indent(s: str) -> str:
    return "\n".join("            " + ln for ln in s.strip().splitlines())


# ---------------------------------------------------------------------------
# route-eval — held-out routing measurement (reports, never gates)
# ---------------------------------------------------------------------------

EVAL_CASES = ROOT / "tests" / "route-eval" / "heldout.jsonl"
FIRED_MARKER = "[polymath-core route]"
# A candidate line: "  - <surface>  (<kind> -- <why>)". Surface ends at the 2-space gap.
CAND_RE = re.compile(r"^\s+-\s+(.+?)\s{2,}\(", re.MULTILINE)


def _eval_run_hook(prompt: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"prompt": prompt}),
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.stdout


def _eval_candidates(out: str) -> list[str]:
    return [m.strip() for m in CAND_RE.findall(out)]


def _eval_load_cases() -> list[dict]:
    rows = []
    for line in EVAL_CASES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _eval_classify(case: dict, fired: bool, cands: list[str]) -> str:
    top = cands[0] if cands else ""
    target = case.get("target", "")
    hit = bool(target) and any(target in c for c in cands)
    top_hit = bool(target) and target in top
    cat = case["category"]
    if cat == "negative":
        return "FALSE-POSITIVE" if fired else "ok-silent"
    if cat == "naturalistic":
        if case["expect"] == "silent":
            # Silence is the by-design outcome; firing on pure prose is the surprise.
            return "fired-unexpected" if fired else "silent-by-design"
        # expect == fire (incidental-token case): score like a token case.
        if not fired:
            return "MISS"
        return "ok-top" if top_hit else ("ok-listed" if hit else "MISROUTE")
    if cat == "token":
        if not fired:
            return "MISS"
        return "ok-top" if top_hit else ("ok-listed" if hit else "MISROUTE")
    if cat == "ambiguous":
        if not fired:
            return "amb-MISS"
        return "amb-top" if top_hit else ("amb-listed" if hit else "amb-other")
    return "?"


def route_eval(emit_json: bool = False) -> int:
    cases = _eval_load_cases()
    results = []
    for c in cases:
        out = _eval_run_hook(c["prompt"])
        fired = FIRED_MARKER in out
        cands = _eval_candidates(out)
        verdict = _eval_classify(c, fired, cands)
        results.append({
            "id": c["id"], "category": c["category"], "expect": c["expect"],
            "fired": fired, "top": cands[0] if cands else "", "candidates": cands,
            "target": c.get("target", ""), "verdict": verdict, "note": c.get("note", ""),
        })

    if emit_json:
        print(json.dumps(results, indent=2))
        return 0

    # ---- human report -------------------------------------------------------
    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    print("HELD-OUT ROUTING MEASUREMENT  (deterministic; no model, no token)")
    print(f"cases: {len(results)}   hook: {HOOK.relative_to(ROOT)}\n")
    for cat in ("token", "ambiguous", "naturalistic", "negative"):
        rows = by_cat.get(cat, [])
        if not rows:
            continue
        print(f"== {cat} ({len(rows)}) ==")
        for r in rows:
            top = r["top"] or "(silent)"
            print(f"  {r['verdict']:<16} {r['id']:<24} -> {top}")
        print()

    # ---- aggregate metrics --------------------------------------------------
    def n(cat, *verdicts):
        return sum(1 for r in by_cat.get(cat, []) if r["verdict"] in verdicts)

    tok = by_cat.get("token", [])
    tok_fire = sum(1 for r in tok if r["fired"])
    tok_correct = n("token", "ok-top", "ok-listed")
    tok_misroute = n("token", "MISROUTE")
    tok_miss = n("token", "MISS")

    nat = by_cat.get("naturalistic", [])
    nat_total = len(nat)
    nat_fired = sum(1 for r in nat if r["fired"])

    neg = by_cat.get("negative", [])
    neg_fp = n("negative", "FALSE-POSITIVE")

    print("== SUMMARY ==")
    if tok:
        print(f"  token precision (fired -> correct surface): {tok_correct}/{tok_fire} fired, "
              f"{tok_miss} silent miss, {tok_misroute} misroute  (of {len(tok)} signalled prompts)")
    if nat:
        print(f"  naturalistic reach (fired at all):           {nat_fired}/{nat_total}  "
              f"-- the rest stay silent by design (no hard signal in natural phrasing)")
    if neg:
        print(f"  false-positive rate on negatives:            {neg_fp}/{len(neg)}")
    print()
    print("  Interpretation: precision/false-positives bound whether a hint, WHEN shown,")
    print("  is trustworthy. Reach bounds how OFTEN a hint appears on real phrasing. Neither")
    print("  measures whether narrowing 149->3 improves the MODEL's pick -- that is Claim B,")
    print("  which needs a live token.")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Triggering tests and held-out routing eval — one subcommand per routing surface."
    )
    top = parser.add_subparsers(dest="surface", required=True)

    skill = top.add_parser(
        "skill", help="skill-triggering tests (naive prompt → right skill)"
    )
    ssub = skill.add_subparsers(dest="cmd", required=True)
    sp = ssub.add_parser("check")
    sp.add_argument("--allow-empty", action="store_true",
                    help="Exit 0 (not 1) when no tests are present.")
    ssub.add_parser("list")
    sp = ssub.add_parser("run")
    sp.add_argument("--timeout", type=int, default=120)
    sp.add_argument("--allow-empty", action="store_true",
                    help="Exit 0 (not 1) when no tests are present.")

    workflow = top.add_parser(
        "workflow", help="workflow-triggering tests (naive prompt → right proposal)"
    )
    wsub = workflow.add_subparsers(dest="cmd", required=True)
    wp = wsub.add_parser("check")
    wp.add_argument("--allow-empty", action="store_true",
                    help="Exit 0 (not 1) when no tests are present.")
    wsub.add_parser("list")
    wp = wsub.add_parser("run")
    wp.add_argument("--timeout", type=int, default=120)
    wp.add_argument("--allow-empty", action="store_true",
                    help="Exit 0 (not 1) when no tests are present.")

    route = top.add_parser(
        "route",
        description="Route-triggering tests (deterministic, no model).",
        help="route-triggering fixtures against the deterministic hook (ROUTE-TRIGGER gate)",
    )
    route.add_argument("mode", choices=["check", "list", "run"], nargs="?", default="check")
    route.add_argument("--allow-empty", action="store_true",
                       help="Exit 0 (not 1) when no fixtures are present.")

    ev = top.add_parser(
        "route-eval",
        description="Held-out routing measurement (no model, no token).",
        help="held-out routing measurement (reports, always exits 0 — not a gate)",
    )
    ev.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    args = parser.parse_args()
    if args.surface == "skill":
        if args.cmd == "check":
            return skill_check(args.allow_empty)
        if args.cmd == "list":
            return skill_list()
        if args.cmd == "run":
            return skill_run(args.timeout, args.allow_empty)
        raise AssertionError(args.cmd)
    if args.surface == "workflow":
        if args.cmd == "check":
            return wf_check(args.allow_empty)
        if args.cmd == "list":
            return wf_list()
        if args.cmd == "run":
            return wf_run(args.timeout, args.allow_empty)
        raise AssertionError(args.cmd)
    if args.surface == "route":
        if args.mode == "list":
            return route_list()
        return {"check": route_check, "run": route_run}[args.mode](args.allow_empty)
    if args.surface == "route-eval":
        return route_eval(args.json)
    raise AssertionError(args.surface)


if __name__ == "__main__":
    raise SystemExit(main())
