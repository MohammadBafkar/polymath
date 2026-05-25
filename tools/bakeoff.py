#!/usr/bin/env python3
"""Run baseline-vs-Polymath bakeoff cases.

`check` validates case files without calling Claude. `run` executes the same
task twice: once as baseline Claude Code, once with the listed Polymath plugins
installed. The scorer is deliberately simple and reproducible: regex-based
rubric items whose weights sum to a decision score.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "tests" / "bakeoff" / "cases"


class CaseError(Exception):
    pass


def load_cases() -> dict[str, tuple[pathlib.Path, dict[str, Any]]]:
    cases: dict[str, tuple[pathlib.Path, dict[str, Any]]] = {}
    for path in sorted(CASES_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        case_id = data.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise CaseError(f"{path}: id is required")
        if case_id in cases:
            raise CaseError(f"{path}: duplicate id {case_id}")
        cases[case_id] = (path, data)
    return cases


def validate_case(path: pathlib.Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("id", "title", "task", "baseline_prompt", "polymath_prompt"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} is required")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins or not all(isinstance(x, str) for x in plugins):
        errors.append("plugins must be a non-empty string list")
    rubric = data.get("rubric")
    if not isinstance(rubric, list) or not rubric:
        errors.append("rubric must be a non-empty list")
    else:
        total = 0
        seen: set[str] = set()
        for i, item in enumerate(rubric):
            if not isinstance(item, dict):
                errors.append(f"rubric[{i}] must be an object")
                continue
            rid = item.get("id")
            if not isinstance(rid, str) or not rid:
                errors.append(f"rubric[{i}].id is required")
            elif rid in seen:
                errors.append(f"rubric[{i}].id duplicates {rid}")
            else:
                seen.add(rid)
            weight = item.get("weight")
            if not isinstance(weight, int) or weight <= 0:
                errors.append(f"rubric[{i}].weight must be a positive integer")
            else:
                total += weight
            patterns = item.get("pass_regex")
            if not isinstance(patterns, list) or not patterns or not all(isinstance(x, str) for x in patterns):
                errors.append(f"rubric[{i}].pass_regex must be a non-empty string list")
            else:
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        errors.append(f"rubric[{i}].pass_regex invalid {pattern!r}: {exc}")
        if total != 10:
            errors.append(f"rubric weights must sum to 10, got {total}")
    threshold = data.get("decision_threshold", {})
    if threshold:
        if not isinstance(threshold, dict):
            errors.append("decision_threshold must be an object")
        else:
            for key in ("minimum_polymath_score", "minimum_delta"):
                if key in threshold and not isinstance(threshold[key], int):
                    errors.append(f"decision_threshold.{key} must be an integer")
    if "timeout_seconds" in data and not isinstance(data["timeout_seconds"], int):
        errors.append("timeout_seconds must be an integer")
    return [f"{path}: {e}" for e in errors]


def check() -> int:
    try:
        cases = load_cases()
    except (json.JSONDecodeError, CaseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    fail = 0
    for path, data in cases.values():
        errors = validate_case(path, data)
        if errors:
            fail = 1
            for err in errors:
                print(f"error: {err}", file=sys.stderr)
        else:
            print(f"OK: {path.relative_to(ROOT)}")
    return fail


def score_output(case: dict[str, Any], output: str) -> dict[str, Any]:
    items = []
    score = 0
    for item in case["rubric"]:
        patterns = item["pass_regex"]
        passed = all(re.search(pattern, output, re.IGNORECASE | re.MULTILINE) for pattern in patterns)
        if passed:
            score += item["weight"]
        items.append(
            {
                "id": item["id"],
                "weight": item["weight"],
                "passed": passed,
                "patterns": patterns,
            }
        )
    return {"score": score, "items": items}


def run_cmd(args: list[str], cwd: pathlib.Path, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def init_scratch() -> pathlib.Path:
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="polymath-bakeoff-"))
    run_cmd(["git", "init", "-q"], scratch, 30)
    run_cmd(["git", "config", "user.email", "ci@polymath.test"], scratch, 30)
    run_cmd(["git", "config", "user.name", "polymath-bakeoff"], scratch, 30)
    (scratch / "README.md").write_text("# Bakeoff scratch\n")
    run_cmd(["git", "add", "."], scratch, 30)
    run_cmd(["git", "commit", "-q", "-m", "init"], scratch, 30)
    return scratch


def run_variant(case: dict[str, Any], variant: str) -> dict[str, Any]:
    if shutil.which("claude") is None:
        raise CaseError("claude CLI not found on PATH")
    scratch = init_scratch()
    timeout = int(case.get("timeout_seconds", 180))
    prompt = case["baseline_prompt"] if variant == "baseline" else case["polymath_prompt"]
    try:
        if variant == "polymath":
            add = run_cmd(["claude", "plugin", "marketplace", "add", str(ROOT)], scratch, 60)
            if add.returncode != 0:
                raise CaseError(f"marketplace add failed:\n{add.stdout}")
            for plugin in case["plugins"]:
                install = run_cmd(["claude", "plugin", "install", f"{plugin}@polymath"], scratch, 60)
                if install.returncode != 0:
                    raise CaseError(f"plugin install failed for {plugin}:\n{install.stdout}")
        result = run_cmd(["claude", "-p", prompt], scratch, timeout)
        output = result.stdout
        scored = score_output(case, output)
        return {
            "variant": variant,
            "returncode": result.returncode,
            "scratch": str(scratch),
            "score": scored["score"],
            "rubric": scored["items"],
            "output": output,
        }
    except Exception:
        shutil.rmtree(scratch, ignore_errors=True)
        raise


def run(case_ids: list[str], out_dir: pathlib.Path) -> int:
    if check() != 0:
        return 1
    cases = load_cases()
    selected = case_ids or sorted(cases)
    out_dir.mkdir(parents=True, exist_ok=True)
    fail = 0
    for case_id in selected:
        if case_id not in cases:
            print(f"error: unknown case {case_id}", file=sys.stderr)
            fail = 1
            continue
        _, case = cases[case_id]
        baseline = run_variant(case, "baseline")
        polymath = run_variant(case, "polymath")
        delta = polymath["score"] - baseline["score"]
        report = {
            "case": case_id,
            "title": case["title"],
            "baseline_score": baseline["score"],
            "polymath_score": polymath["score"],
            "delta": delta,
            "threshold": case.get("decision_threshold", {}),
            "results": {"baseline": baseline, "polymath": polymath},
        }
        path = out_dir / f"{case_id}.json"
        path.write_text(json.dumps(report, indent=2))
        threshold = case.get("decision_threshold", {})
        min_score = int(threshold.get("minimum_polymath_score", 0))
        min_delta = int(threshold.get("minimum_delta", 0))
        passed = polymath["score"] >= min_score and delta >= min_delta
        print(
            f"{case_id}: baseline={baseline['score']} polymath={polymath['score']} "
            f"delta={delta} -> {'PASS' if passed else 'FAIL'}"
        )
        if not passed:
            fail = 1
    return fail


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("check")
    run_p = sub.add_parser("run")
    run_p.add_argument("case", nargs="*", help="Case id(s); default: all")
    run_p.add_argument("--out-dir", default=".pdata/bakeoff", help="Where JSON reports are written")
    args = parser.parse_args()

    if args.command in {None, "check"}:
        return check()
    if args.command == "run":
        return run(args.case, ROOT / args.out_dir)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
