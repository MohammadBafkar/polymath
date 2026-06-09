#!/usr/bin/env python3
"""Route-triggering tests.

A route-triggering test asserts that the *deterministic* ambient routing hook
(`plugins/polymath-core/hooks/scripts/route-hint.py`) proposes the right
Polymath surface for a given prompt — or correctly stays silent.

Unlike skill-triggering / workflow-triggering, this harness needs **no model
and no token**: the hook's output is a pure function of the prompt text and the
bundled signal table. `run` mode therefore executes in CI on every PR and makes
routing precision a gateable metric (a regression in the table or the scorer
fails the build).

Test file shape: `tests/route-triggering/<id>.md`

```markdown
---
prompt: "Review this PR https://github.com/acme/web/pull/42 for correctness."
must_appear:
  - "polymath-flows:run-workflow reviewPR"
must_not_appear:        # optional
  - "respondToIncident"
---
Why this fixture exists.
```

Negative (must-stay-silent) fixture:

```markdown
---
prompt: "What's the capital of France?"
expect_silent: true
---
```

Run modes:

  check  — validate every fixture's frontmatter (no execution).
  list   — print one row per fixture.
  run    — pipe each prompt through route-hint.py and assert the expectations.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests" / "route-triggering"
HOOK = ROOT / "plugins" / "polymath-core" / "hooks" / "scripts" / "route-hint.py"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _load_yaml(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text)
    # Minimal shim: scalars + simple `- ` lists, enough for these fixtures.
    out: dict[str, Any] = {}
    key = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.lstrip().startswith("- ") and key:
            out.setdefault(key, []).append(_scalar(raw.lstrip()[2:].strip()))
            continue
        if ":" in raw:
            k, _, v = raw.partition(":")
            key = k.strip()
            v = v.strip()
            out[key] = _scalar(v) if v else []
    return out


def _scalar(v: str) -> Any:
    v = v.strip().strip('"').strip("'")
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v


def parse_fixture(path: pathlib.Path) -> dict:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path.name}: missing YAML frontmatter")
    fm = _load_yaml(m.group(1)) or {}
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
    return {
        "id": path.stem,
        "prompt": fm["prompt"],
        "expect_silent": silent,
        "must_appear": must,
        "must_not_appear": not_must,
    }


def fixtures() -> list[pathlib.Path]:
    if not TESTS_DIR.is_dir():
        return []
    return sorted(TESTS_DIR.glob("*.md"))


def _no_fixtures(label: str, glob: str, allow_empty: bool) -> int:
    """A gate with zero fixtures is a silent no-op, not a pass. Fail by
    default so a deleted/moved fixture set can't make this gate green."""
    if allow_empty:
        print(f"{label}: no fixtures found ({glob}) — allowed by --allow-empty")
        return 0
    print(
        f"{label}: no fixtures found ({glob}) — refusing to pass an empty gate "
        f"(pass --allow-empty to override)",
        file=sys.stderr,
    )
    return 1


def run_hook(prompt: str) -> str:
    payload = json.dumps({"prompt": prompt})
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.stdout


def cmd_check(allow_empty: bool = False) -> int:
    files = fixtures()
    if not files:
        return _no_fixtures("route-triggering check", "tests/route-triggering/*.md", allow_empty)
    errs = []
    for f in files:
        try:
            parse_fixture(f)
        except Exception as e:  # noqa: BLE001
            errs.append(str(e))
    for e in errs:
        print(f"  FAIL  {e}")
    print(f"route-triggering check: {len(files)} fixture(s), {len(errs)} error(s)")
    return 1 if errs else 0


def cmd_list() -> int:
    for f in fixtures():
        try:
            fx = parse_fixture(f)
        except Exception as e:  # noqa: BLE001
            print(f"  (invalid) {f.name}: {e}")
            continue
        kind = "silent" if fx["expect_silent"] else "expect"
        target = "—" if fx["expect_silent"] else ", ".join(fx["must_appear"])
        print(f"  {fx['id']:<28} {kind:<7} {target}")
    return 0


def cmd_run(allow_empty: bool = False) -> int:
    if not HOOK.exists():
        print(f"route-triggering run: hook not found at {HOOK}", file=sys.stderr)
        return 1
    files = fixtures()
    if not files:
        return _no_fixtures("route-triggering run", "tests/route-triggering/*.md", allow_empty)
    passed = failed = 0
    for f in files:
        try:
            fx = parse_fixture(f)
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  {f.name}: {e}")
            failed += 1
            continue
        out = run_hook(fx["prompt"])
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Route-triggering tests (deterministic, no model).")
    ap.add_argument("mode", choices=["check", "list", "run"], nargs="?", default="check")
    ap.add_argument("--allow-empty", action="store_true",
                    help="Exit 0 (not 1) when no fixtures are present.")
    args = ap.parse_args()
    if args.mode == "list":
        return cmd_list()
    return {"check": cmd_check, "run": cmd_run}[args.mode](args.allow_empty)


if __name__ == "__main__":
    sys.exit(main())
