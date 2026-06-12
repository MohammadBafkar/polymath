#!/usr/bin/env bash
# polymath-core SessionStart hook
#
# Surfaces (quietly):
#   1. Project context loaded from .polymath/project.yaml — one line.
#   2. Paused flows-lite workflow runs.
#   3. "Due now" items from the scheduled-work queue
#      (${CLAUDE_PLUGIN_DATA}/polymath-core/queue.json — § 11.6).
#
# Polymath does not ship a scheduler. Whoever owns the schedule
# (Anthropic Cloud Routine, GitHub Action, OS cron, …) writes to
# queue.json; this hook only renders entries whose `due` is in the
# past relative to wall-clock time.
#
# Quiet by default — only prints when there is something to surface.
set -euo pipefail

data_root="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}"
script_dir="$(cd "$(dirname "$0")" && pwd)"

# The hook payload arrives once on stdin; capture it for the consumers below.
hook_payload="$(cat 2>/dev/null || true)"

# --- repo evidence (routing repo_state probes) ---
# Cache declared repo-state probes (route-signals.json `repo_probes` +
# project overlay) as booleans for route-hint's +1 soft boost. Bounded
# (≤64 probes / 200ms) and fail-open: never blocks, never prints.
if command -v python3 >/dev/null 2>&1 && [[ -f "${script_dir}/write-repo-evidence.py" ]]; then
  printf '%s' "$hook_payload" | python3 "${script_dir}/write-repo-evidence.py" >/dev/null 2>&1 || true
fi

# --- project context ---
# Refresh the project-context snapshot under
# ${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json from
# .polymath/project.yaml (project → user → home). The loader script
# prints a one-line summary on stdout when a project file exists; we
# capture it and surface alongside the other notes below. A bad project
# file fails the loader with exit 2 — surface the validation errors so
# the user notices but continue the hook (other surfaces still run).
project_summary=""
if [[ -x "${script_dir}/load-project-context.py" ]]; then
  if loader_out="$(python3 "${script_dir}/load-project-context.py" 2>&1)"; then
    project_summary="$loader_out"
  else
    # Loader failed; pass through its stderr so the user sees why.
    echo "$loader_out" >&2
  fi
fi

# --- first-run nudge ---
# The highest-leverage onboarding moment is a fresh session in an
# un-initialized repo: without this, the loader exits silently and the user
# gets no signal that init-project exists. Surface exactly one suppressible
# line when no project file resolved AND we are inside a git repo we have not
# nudged before. Naturally suppressed once initialized (the loader then emits
# a summary) and suppressed per-repo via the marker so it never nags.
# If python3 is absent the loader, workflows, and most tooling are degraded.
# Surface one actionable line instead of failing silently, and prefer it over
# the init nudge (which points at init-project, itself needing python3).
py_note=""
if ! command -v python3 >/dev/null 2>&1; then
  py_note="Polymath: python3 not found — project context, workflows, and hooks are degraded. Run /polymath-core:doctor."
fi

init_nudge=""
if [[ -z "$project_summary" && -z "$py_note" ]] && command -v git >/dev/null 2>&1; then
  repo_root="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$repo_root" ]]; then
    nudge_marker="${data_root}/polymath-core/init-nudged"
    if [[ ! -f "$nudge_marker" ]] || ! grep -Fxq "$repo_root" "$nudge_marker" 2>/dev/null; then
      init_nudge="Polymath: this repo isn't initialized. Run /polymath-core:init-project to set up project context (or /polymath-core:doctor to check your tools)."
      { mkdir -p "$(dirname "$nudge_marker")" && printf '%s\n' "$repo_root" >> "$nudge_marker"; } || true
    fi
  fi
fi

# --- paused workflows ---
flows_workflows_dir="${data_root}/polymath-flows/workflows"
# Older layouts wrote to ${data_root}/workflows; fall back if needed.
if [[ ! -d "$flows_workflows_dir" && -d "${data_root}/workflows" ]]; then
  flows_workflows_dir="${data_root}/workflows"
fi

# Surface resumable runs: paused (need attention) AND active (in-progress across
# sessions). An active run was previously invisible here, so an interrupted run
# (context death, /clear, closed tab) looked orphaned; we now surface it and flag
# it stale when last_active is >= 2 days old.
flows_section=""
if [[ -d "$flows_workflows_dir" ]]; then
  flows_section="$(python3 - "$flows_workflows_dir" <<'PY' 2>/dev/null || true
import json, sys, pathlib, datetime
base = pathlib.Path(sys.argv[1])
now = datetime.datetime.now(datetime.timezone.utc)
def parse(ts):
    if not ts:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H-%M"):
        try:
            d = datetime.datetime.strptime(ts, fmt)
            return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None
paused, active = [], []
for sp in sorted(base.glob("*/state.json")):
    try:
        s = json.loads(sp.read_text())
    except Exception:
        continue
    st = s.get("status")
    rid = s.get("run_id", sp.parent.name)
    if st == "paused":
        paused.append((rid, s.get("pause_reason", "")))
    elif st == "active":
        la = parse(s.get("last_active") or s.get("started"))
        inflight = s.get("in_flight") or {}
        active.append((rid, (now - la).days if la else None, inflight.get("step")))
out = []
if paused:
    out.append(f"Polymath: {len(paused)} paused workflow(s):")
    for rid, reason in paused[:5]:
        tail = f" — {reason}" if reason else ""
        out.append(f"  - {rid}{tail}  (resume: /polymath-flows:resume-workflow {rid})")
    if len(paused) > 5:
        out.append(f"  …and {len(paused) - 5} more")
if active:
    if paused:
        out.append("")
    out.append(f"Polymath: {len(active)} in-progress workflow(s):")
    for rid, age, step in active[:5]:
        stale = f", stale ({age}d)" if (age is not None and age >= 2) else ""
        mid = f", mid-step: {step}" if step else ""
        out.append(f"  - {rid}{stale}{mid}  (continue: /polymath-flows:resume-workflow {rid})")
    if len(active) > 5:
        out.append(f"  …and {len(active) - 5} more")
print("\n".join(out))
PY
)"
fi

# --- scheduled-work queue ---
queue_file="${data_root}/polymath-core/queue.json"
due_now="$(python3 - "$queue_file" 2>/dev/null <<'PY' || true
import json, pathlib, sys, datetime
p = pathlib.Path(sys.argv[1])
if not p.exists():
    sys.exit(0)
try:
    items = json.loads(p.read_text())
except Exception:
    sys.exit(0)
if not isinstance(items, list):
    sys.exit(0)
now = datetime.datetime.now(datetime.timezone.utc)
out = []
for it in items:
    due = it.get("due")
    if not due:
        continue
    try:
        when = datetime.datetime.fromisoformat(due.replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        continue
    if when <= now:
        skill = it.get("skill") or "?"
        note = it.get("note") or ""
        out.append(f"  - {it.get('id','(no id)')}  → {skill}  {note}".rstrip())
print("\n".join(out))
PY
)"

# --- render ---
emitted=0
if [[ -n "$project_summary" ]]; then
  echo "$project_summary"
  emitted=1
fi
if [[ -n "$py_note" ]]; then
  [[ $emitted -eq 1 ]] && echo
  echo "$py_note"
  emitted=1
fi
if [[ -n "$init_nudge" ]]; then
  [[ $emitted -eq 1 ]] && echo
  echo "$init_nudge"
  emitted=1
fi
if [[ -n "$flows_section" ]]; then
  [[ $emitted -eq 1 ]] && echo
  printf '%s\n' "$flows_section"
  emitted=1
fi
if [[ -n "$due_now" ]]; then
  [[ $emitted -eq 1 ]] && echo
  echo "Polymath scheduled work due now:"
  printf "%s\n" "$due_now"
fi

exit 0
