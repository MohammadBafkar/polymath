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
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
BAKEOFF_ROOT = ROOT / "tests" / "bakeoff"
LEGACY_CASES_DIR = BAKEOFF_ROOT / "cases"


class CaseError(Exception):
    pass


def _discover_case_paths() -> list[pathlib.Path]:
    """Find every bakeoff case file under tests/bakeoff/.

    The current layout is `tests/bakeoff/<plugin>/<scenario>/case.json`
    (per-scenario eval files, vally-style). The legacy layout
    `tests/bakeoff/cases/*.json` is also accepted so external case
    repos do not break — paths there continue to load with no
    plugin/scenario inference. Cases under a recognised plugin
    directory have their plugin + scenario derived from the path.
    """
    paths: list[pathlib.Path] = []
    if LEGACY_CASES_DIR.is_dir():
        paths.extend(sorted(LEGACY_CASES_DIR.glob("*.json")))
    for case in sorted(BAKEOFF_ROOT.rglob("case.json")):
        if LEGACY_CASES_DIR in case.parents:
            continue  # already collected by legacy glob
        paths.append(case)
    return paths


def load_cases() -> dict[str, tuple[pathlib.Path, dict[str, Any]]]:
    cases: dict[str, tuple[pathlib.Path, dict[str, Any]]] = {}
    for path in _discover_case_paths():
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
    if "effort" in data and data["effort"] not in {"low", "medium", "high", "xhigh", "max"}:
        errors.append("effort must be one of: low, medium, high, xhigh, max")
    if "disable_tools" in data and not isinstance(data["disable_tools"], bool):
        errors.append("disable_tools must be a boolean")
    errors.extend(_check_rubric_leakage(data))
    return [f"{path}: {e}" for e in errors]


_REGEX_META = re.compile(r"[.?*+\\(){}\[\]^$]")


def _rubric_alternatives(rubric: list[Any]) -> list[tuple[str, str]]:
    """Yield (rubric_id, literal_token) pairs for every alternative in every
    pass_regex. Regex metacharacters are stripped; tokens shorter than 3
    characters are dropped to avoid noise from words like 'or'."""
    out: list[tuple[str, str]] = []
    for item in rubric:
        if not isinstance(item, dict):
            continue
        rid = item.get("id", "?")
        for pattern in item.get("pass_regex") or []:
            for alt in pattern.split("|"):
                token = _REGEX_META.sub("", alt).strip()
                if len(token) >= 3:
                    out.append((rid, token))
    return out


def _check_rubric_leakage(data: dict[str, Any]) -> list[str]:
    """A bakeoff is gameable if the polymath_prompt contains rubric pass-tokens
    that the baseline_prompt does not. The polymath side then earns points the
    baseline cannot, regardless of model quality. The honest contract: both
    prompts share the same domain context; the only difference is the
    'Use Polymath <X>' hint. Rubric tokens may appear in BOTH prompts (they
    are part of the shared input) or in NEITHER (the rubric tests output
    quality); they may not appear in only one.

    Reports asymmetric appearances. Polymath-only is an error (engineered
    advantage). Baseline-only is also an error (biased against Polymath)."""
    rubric = data.get("rubric") or []
    bp = (data.get("baseline_prompt") or "").lower()
    pp = (data.get("polymath_prompt") or "").lower()
    if not bp or not pp:
        return []
    errors: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for rid, token in _rubric_alternatives(rubric):
        tk = token.lower()
        in_b = tk in bp
        in_p = tk in pp
        if in_p and not in_b:
            key = (rid, tk, "polymath-only")
            if key not in seen:
                errors.append(
                    f"rubric leak: pass-token {token!r} (rubric {rid!r}) appears "
                    f"in polymath_prompt but not in baseline_prompt — engineered "
                    f"advantage for Polymath"
                )
                seen.add(key)
        elif in_b and not in_p:
            key = (rid, tk, "baseline-only")
            if key not in seen:
                errors.append(
                    f"rubric leak: pass-token {token!r} (rubric {rid!r}) appears "
                    f"in baseline_prompt but not in polymath_prompt — biased "
                    f"against Polymath"
                )
                seen.add(key)
    return errors


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
    """Regex-based pre-filter — does the output engage with the task at all.

    Kept alongside the LLM judge because it costs nothing, runs
    deterministically, and catches the "model refused / output is empty"
    case without an LLM round-trip. The LLM-judge in `score_with_judge` is
    the source of truth for ranking quality; the regex score is a hard
    floor: zero regex score = the run did not engage with the prompt.
    """
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


# ---------------------------------------------------------------------------
# LLM-judge scoring
# ---------------------------------------------------------------------------

# Judge model id. Overridable via env so re-enabling the (currently disabled)
# live bakeoff CI doesn't silently break if this alias retires — set
# POLYMATH_BAKEOFF_JUDGE_MODEL to pin a current model.
JUDGE_MODEL = os.environ.get("POLYMATH_BAKEOFF_JUDGE_MODEL", "claude-sonnet-4-6")
JUDGE_PROMPT_FILE = ROOT / "tools" / "bakeoff" / "judge-prompt.md"
CALIBRATION_DIR = ROOT / "tools" / "bakeoff" / "calibration"
JUDGE_DRIFT_TOLERANCE = 1  # judge-vs-human delta > 1 ⇒ recalibrate


def _judge_prompt_template() -> str:
    if not JUDGE_PROMPT_FILE.exists():
        raise CaseError(f"judge prompt not found: {JUDGE_PROMPT_FILE}")
    return JUDGE_PROMPT_FILE.read_text()


def _build_judge_input(case: dict[str, Any], output: str) -> str:
    """Compose the user-message body for the judge call.

    The judge sees the rubric (id + weight + advisory regex hints) plus the
    output to score. The full judge contract lives in `judge-prompt.md`; we
    stick that prompt verbatim in front of the task + rubric + output so the
    grading rules are pinned across runs.
    """
    rubric_view = [
        {
            "id": item.get("id"),
            "weight": item.get("weight"),
            "hint_tokens": item.get("pass_regex", []),
        }
        for item in case.get("rubric") or []
    ]
    payload = {
        "task": case.get("task", ""),
        "rubric": rubric_view,
        "output": output,
    }
    return (
        _judge_prompt_template()
        + "\n\n# Input\n\n"
        + "```json\n"
        + json.dumps(payload, indent=2)
        + "\n```\n"
    )


def _parse_judge_response(text: str) -> dict[str, Any]:
    """Extract the first JSON object from the judge response.

    The judge contract requires a bare JSON object. Strict parsing first;
    if that fails (the model wrapped it in a fence or prose), find the
    outermost {...} substring and parse that. Returns a normalised dict
    with score/per_item/summary fields and an `error` key when parsing
    failed entirely.
    """
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return {
                "score": 0,
                "per_item": [],
                "summary": "judge output unparseable",
                "error": "no JSON object found",
                "raw": text,
            }
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError as e:
            return {
                "score": 0,
                "per_item": [],
                "summary": "judge output unparseable",
                "error": f"JSONDecodeError: {e}",
                "raw": text,
            }
    score = data.get("score")
    if not isinstance(score, int) or not 0 <= score <= 10:
        data["error"] = f"invalid score: {score!r}"
        data["score"] = 0
    if "per_item" not in data or not isinstance(data["per_item"], list):
        data["per_item"] = []
    if "summary" not in data or not isinstance(data["summary"], str):
        data["summary"] = ""
    return data


def score_with_judge(
    case: dict[str, Any], output: str, *, timeout: int = 120
) -> dict[str, Any]:
    """Run the LLM judge against an output. Returns the parsed response.

    Skips the judge entirely (and returns a clearly-marked stub) when the
    `claude` CLI is unavailable so the bakeoff is still runnable in a
    no-CLI dev environment. The caller decides whether to fall back to the
    regex score in that case.
    """
    if shutil.which("claude") is None:
        return {
            "score": None,
            "per_item": [],
            "summary": "judge skipped: claude CLI not on PATH",
            "skipped": True,
        }
    judge_input = _build_judge_input(case, output)
    args = [
        "claude",
        "-p",
        "--permission-mode",
        "dontAsk",
        "--no-session-persistence",
        "--tools",
        "",  # judge needs no tools; bound the action space
        "--model",
        JUDGE_MODEL,
        judge_input,
    ]
    result = run_cmd(args, ROOT, timeout)
    parsed = _parse_judge_response(result.stdout or "")
    parsed["returncode"] = result.returncode
    if result.returncode != 0 and "error" not in parsed:
        parsed["error"] = f"judge exited {result.returncode}"
    return parsed


def calibrate() -> int:
    """Compare the judge against frozen human-blind gold scores.

    A calibration record at `tools/bakeoff/calibration/<id>.json` is:

        {
          "case_id": "<existing case id>",
          "scenario": "<short label>",
          "output": "<frozen model output>",
          "gold_score": <int 0-10>,
          "gold_note": "<why this score is the gold>"
        }

    The command runs the judge against each record and prints the
    judge score, the gold score, and the delta. Exits 1 when any
    |delta| > JUDGE_DRIFT_TOLERANCE.
    """
    cases = load_cases()
    if not CALIBRATION_DIR.is_dir():
        print(
            f"info: no calibration set at {CALIBRATION_DIR.relative_to(ROOT)} "
            f"(create one to enable judge drift checks)"
        )
        return 0
    drift = 0
    seen = 0
    for path in sorted(CALIBRATION_DIR.glob("*.json")):
        record = json.loads(path.read_text())
        case_id = record.get("case_id")
        if not isinstance(case_id, str) or case_id not in cases:
            print(f"::warning::{path.name}: unknown case_id {case_id!r}; skipping")
            continue
        gold = record.get("gold_score")
        if not isinstance(gold, int) or not 0 <= gold <= 10:
            print(f"::warning::{path.name}: invalid gold_score {gold!r}; skipping")
            continue
        _, case_data = cases[case_id]
        judged = score_with_judge(case_data, record.get("output", ""))
        seen += 1
        if judged.get("skipped"):
            print(f"{path.name}: judge skipped — {judged.get('summary')}")
            continue
        delta = (judged.get("score") or 0) - gold
        marker = "OK" if abs(delta) <= JUDGE_DRIFT_TOLERANCE else "DRIFT"
        if marker == "DRIFT":
            drift += 1
        print(
            f"{path.name}: gold={gold} judge={judged.get('score')} "
            f"delta={delta:+d} {marker}"
        )
    if seen == 0:
        print("info: no calibration records found")
        return 0
    if drift:
        print(f"calibrate: {drift} record(s) drifted > {JUDGE_DRIFT_TOLERANCE}")
        return 1
    print(f"calibrate: {seen} record(s) within tolerance ±{JUDGE_DRIFT_TOLERANCE}")
    return 0


def run_cmd(args: list[str], cwd: pathlib.Path, timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if exc.stderr:
            output += exc.stderr
        output += f"\n[TIMEOUT after {timeout}s]\n"
        return subprocess.CompletedProcess(args, 124, output, None)


def init_scratch() -> pathlib.Path:
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="polymath-bakeoff-"))
    run_cmd(["git", "init", "-q"], scratch, 30)
    run_cmd(["git", "config", "user.email", "ci@polymath.test"], scratch, 30)
    run_cmd(["git", "config", "user.name", "polymath-bakeoff"], scratch, 30)
    (scratch / "README.md").write_text("# Bakeoff scratch\n")
    run_cmd(["git", "add", "."], scratch, 30)
    run_cmd(["git", "commit", "-q", "-m", "init"], scratch, 30)
    return scratch


def run_variant(case: dict[str, Any], variant: str, *, use_judge: bool = False) -> dict[str, Any]:
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
        args = [
            "claude",
            "-p",
            "--permission-mode",
            "dontAsk",
            "--no-session-persistence",
        ]
        if case.get("disable_tools", True):
            args.extend(["--tools", ""])
        effort = case.get("effort", "low")
        args.extend(["--effort", effort, prompt])
        result = run_cmd(args, scratch, timeout)
        output = result.stdout
        scored = score_output(case, output)
        record = {
            "variant": variant,
            "returncode": result.returncode,
            "scratch": str(scratch),
            "score": scored["score"],
            "rubric": scored["items"],
            "output": output,
        }
        if use_judge:
            record["judge"] = score_with_judge(case, output)
        return record
    except Exception:
        shutil.rmtree(scratch, ignore_errors=True)
        raise


def run(case_ids: list[str], out_dir: pathlib.Path, *, use_judge: bool = False) -> int:
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
        print(f"{case_id}: running baseline", flush=True)
        baseline = run_variant(case, "baseline", use_judge=use_judge)
        print(f"{case_id}: running polymath", flush=True)
        polymath = run_variant(case, "polymath", use_judge=use_judge)
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
        if use_judge:
            b_judge = (baseline.get("judge") or {}).get("score")
            p_judge = (polymath.get("judge") or {}).get("score")
            report["judge"] = {
                "baseline_score": b_judge,
                "polymath_score": p_judge,
                "delta": (
                    (p_judge - b_judge)
                    if isinstance(b_judge, int) and isinstance(p_judge, int)
                    else None
                ),
            }
        path = out_dir / f"{case_id}.json"
        path.write_text(json.dumps(report, indent=2))
        threshold = case.get("decision_threshold", {})
        min_score = int(threshold.get("minimum_polymath_score", 0))
        min_delta = int(threshold.get("minimum_delta", 0))
        passed = (
            baseline["returncode"] == 0
            and polymath["returncode"] == 0
            and polymath["score"] >= min_score
            and delta >= min_delta
        )
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
    run_p.add_argument(
        "--judge",
        action="store_true",
        help="Also score each variant with the pinned LLM judge (see tools/bakeoff/judge-prompt.md).",
    )
    sub.add_parser(
        "calibrate",
        help="Re-run the judge against the frozen calibration set and report drift.",
    )
    args = parser.parse_args()

    if args.command in {None, "check"}:
        return check()
    if args.command == "run":
        use_judge = bool(args.judge) or os.environ.get("POLYMATH_BAKEOFF_JUDGE") == "1"
        return run(args.case, ROOT / args.out_dir, use_judge=use_judge)
    if args.command == "calibrate":
        return calibrate()
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
