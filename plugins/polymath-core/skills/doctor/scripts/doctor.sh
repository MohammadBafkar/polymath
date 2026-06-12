#!/usr/bin/env bash
# polymath-core:doctor — preflight environment check.
#
# Reports PASS / WARN / FAIL for the tools Polymath relies on, plus the
# validity of any .polymath/project.yaml in the current repo. Exits non-zero
# only when a REQUIRED tool is missing, so it can gate init-project as step 0.
#
# Required:    bash, python3
# Recommended: git (workflows + first-run nudge), claude CLI (strict validate,
#              live golden fixtures)
# Optional:    PyYAML (the loader has a hand-rolled fallback), jq
set -uo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
loader="${script_dir}/../../../hooks/scripts/load-project-context.py"

req_fail=0
pass() { printf '  ✓ %-10s %s\n' "$1" "$2"; }
warn() { printf '  ! %-10s %s\n' "$1" "$2"; }
fail() { printf '  ✗ %-10s %s\n' "$1" "$2"; }

echo "polymath-core:doctor — environment preflight"
echo
echo "Required:"
if command -v bash >/dev/null 2>&1; then
  pass "bash" "$(bash --version 2>/dev/null | head -1)"
else
  fail "bash" "not found — install bash"; req_fail=1
fi
if command -v python3 >/dev/null 2>&1; then
  pass "python3" "$(python3 --version 2>&1)"
else
  fail "python3" "not found — install Python 3 (hooks, loader, and tools need it)"; req_fail=1
fi

echo
echo "Recommended:"
if command -v git >/dev/null 2>&1; then
  pass "git" "$(git --version 2>&1)"
else
  warn "git" "not found — workflows and the first-run nudge need a git repo"
fi
if command -v claude >/dev/null 2>&1; then
  pass "claude" "$(claude --version 2>&1 | head -1)"
else
  warn "claude" "not found — needed for 'claude plugin validate --strict' and live golden fixtures"
fi

echo
echo "Optional:"
if command -v python3 >/dev/null 2>&1 && python3 -c "import yaml" >/dev/null 2>&1; then
  pass "PyYAML" "present (richer project.yaml parsing)"
else
  warn "PyYAML" "absent — the loader falls back to a minimal parser; fine for simple files"
fi
if command -v jq >/dev/null 2>&1; then
  pass "jq" "$(jq --version 2>&1)"
else
  warn "jq" "absent — not required by Polymath; handy for inspecting JSON snapshots"
fi

echo
echo "Project context:"
if [[ -f ".polymath/project.yaml" ]]; then
  if command -v python3 >/dev/null 2>&1 && [[ -x "$loader" ]]; then
    tmp_data="$(mktemp -d)"
    if out="$(CLAUDE_PLUGIN_DATA="$tmp_data" python3 "$loader" 2>&1)"; then
      pass "project.yaml" "valid — ${out#Polymath: }"
    else
      fail "project.yaml" "present but the loader rejected it:"
      printf '%s\n' "$out" | sed 's/^/      /'
      # A bad project file is a real problem, but not a missing-tool failure;
      # surface it without failing the required-tools gate.
    fi
    rm -rf "$tmp_data"
  else
    warn "project.yaml" "present (cannot validate — python3 or loader unavailable)"
  fi
else
  warn "project.yaml" "not found — run /polymath-core:init-project to create it"
fi

echo
echo "Routing pipeline:"
# Locate the sibling polymath-pipeline engine in either layout:
# repo checkout (plugins/<name>/…) or install cache (…/polymath/<name>/<ver>/…).
core_root="$(cd "${script_dir}/../../.." && pwd)"
parent="$(dirname "$core_root")"
pipeline_bin=""
if [[ "$(basename "$parent")" == "plugins" ]]; then
  cand="${parent}/polymath-pipeline/bin/polymath-pipeline"
  [[ -f "$cand" ]] && pipeline_bin="$cand"
else
  for cand in "$(dirname "$parent")"/polymath-pipeline/*/bin/polymath-pipeline \
              "$(dirname "$parent")"/polymath-pipeline/bin/polymath-pipeline; do
    [[ -f "$cand" ]] && pipeline_bin="$cand"
  done
fi
if [[ -z "$pipeline_bin" ]]; then
  warn "routing" "polymath-pipeline not installed — routing.mode classify/enforce would be inert; ambient hints only"
elif ! command -v python3 >/dev/null 2>&1; then
  warn "routing" "cannot inspect (python3 unavailable)"
else
  status_json="$(python3 "$pipeline_bin" status --cwd . 2>/dev/null || echo '{}')"
  POLYMATH_DOCTOR_STATUS="$status_json" python3 - <<'PY'
import json, os

try:
    doc = json.loads(os.environ.get("POLYMATH_DOCTOR_STATUS") or "{}")
except Exception:
    doc = {}
mode = doc.get("mode") or "hint"
errs = doc.get("config_errors") or []
kill = doc.get("kill_switch")
events = doc.get("recent_events") or {}
window = doc.get("recent_event_window") or 0


def line(sym: str, label: str, msg: str) -> None:
    print(f"  {sym} {label:<10} {msg}")


if errs:
    line("✗", "routing", f"mode={mode} with {len(errs)} config error(s):")
    for e in errs:
        print(f"      {e}")
elif mode == "hint":
    line("✓", "routing", "mode=hint — ambient route hints only "
         "(declare routing.mode classify|enforce in .polymath/project.yaml to opt in)")
else:
    line("✓", "routing", f"mode={mode} — polymath-pipeline active")
if kill:
    line("!", "routing", f"kill switch engaged via {kill} (audited)")
interesting = {k: events[k] for k in
               ("enforce-deny", "kill-switch", "fail-open", "mark-rejected", "config-error",
                "policy-overlay-ignored", "policy-overlay-invalid")
               if events.get(k)}
if interesting:
    summary = ", ".join(f"{k}×{v}" for k, v in sorted(interesting.items()))
    line("!", "decisions", f"last {window} log lines for this root: {summary}")
elif mode != "hint":
    line("✓", "decisions", f"no denials, fail-opens, or kill-switch uses in the last {window} log lines")

# Hint-adoption telemetry (opt-in, POLYMATH_TELEMETRY=1): join emitted
# hints (polymath-core hint-log.jsonl, surface names only) against
# `classified` mark events within a 30-minute window — the proxy for
# "hint emitted ⇒ surface invoked within N turns".
import datetime, pathlib

base = pathlib.Path(os.environ.get("CLAUDE_PLUGIN_DATA")
                    or pathlib.Path.home() / ".claude" / "plugins" / "data")
hint_log = (base if base.name == "polymath-core" else base / "polymath-core") / "hint-log.jsonl"
if hint_log.is_file():
    def parse_ts(value):
        try:
            return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except Exception:
            return None

    marks = []
    for cand in (base / "decisions.jsonl",
                 base / "polymath-pipeline" / "decisions.jsonl"):
        if cand.is_file():
            for raw in cand.read_text(errors="ignore").splitlines()[-1000:]:
                try:
                    ev = json.loads(raw)
                except Exception:
                    continue
                if isinstance(ev, dict) and ev.get("event") == "classified":
                    ts = parse_ts(ev.get("ts"))
                    if ts and ev.get("surface"):
                        marks.append((ts, ev["surface"]))
            break
    emissions = []
    for raw in hint_log.read_text(errors="ignore").splitlines()[-200:]:
        try:
            ev = json.loads(raw)
        except Exception:
            continue
        ts = parse_ts(ev.get("ts")) if isinstance(ev, dict) else None
        if ts and ev.get("surfaces"):
            emissions.append((ts, ev["surfaces"]))
    adopted = 0
    for ts, surfaces in emissions:
        if any(0 <= (mts - ts).total_seconds() <= 1800
               and any(s in msurf or msurf in s for s in surfaces)
               for mts, msurf in marks):
            adopted += 1
    if emissions:
        line("✓", "adoption", f"{adopted}/{len(emissions)} recent hint emission(s) followed "
             f"by a matching mark within 30m (telemetry opt-in)")
PY
fi

# --- workflow injection tiering (written by polymath-flows at SessionStart) ---
tiering_file="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}/polymath-flows/workflow-index.project.json"
if [[ -f "$tiering_file" ]] && command -v python3 >/dev/null 2>&1; then
  echo
  echo "Workflow injection:"
  POLYMATH_DOCTOR_TIERING="$tiering_file" python3 - <<'PY'
import json, os

try:
    doc = json.loads(open(os.environ["POLYMATH_DOCTOR_TIERING"]).read())
except Exception:
    doc = {}
t = doc.get("tiering") or {}
if not t:
    print("  ! tiering    no tiering record yet (pre-tiering session data)")
else:
    tier_a = t.get("tier_a") or []
    relevant = t.get("relevant") or []
    overflow = t.get("overflow_relevant") or []
    print(f"  ✓ tiering    tier A {len(tier_a)} workflow(s) "
          f"({len(relevant)} repo-relevant), tier B {t.get('tier_b_count', 0)} via pointer "
          f"(budget {t.get('budget_tokens', '?')} tokens)")
    if overflow:
        print(f"  ! tiering    repo-relevant but did not fit tier A: {', '.join(overflow)} "
              f"— trim whenToUse lines or revisit the budget")
PY
fi

echo
if [[ "$req_fail" -ne 0 ]]; then
  echo "doctor: FAILED — a required tool is missing (see ✗ above)."
  exit 1
fi
echo "doctor: OK — required tools present."
exit 0
