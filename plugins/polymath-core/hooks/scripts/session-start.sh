#!/usr/bin/env bash
# polymath-core SessionStart hook
#
# Surfaces (quietly):
#   1. Paused flows-lite workflow runs.
#   2. "Due now" items from the scheduled-work queue
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

# --- paused workflows ---
flows_workflows_dir="${data_root}/polymath-flows/workflows"
# Older layouts wrote to ${data_root}/workflows; fall back if needed.
if [[ ! -d "$flows_workflows_dir" && -d "${data_root}/workflows" ]]; then
  flows_workflows_dir="${data_root}/workflows"
fi

paused=()
if [[ -d "$flows_workflows_dir" ]]; then
  while IFS= read -r state; do
    status="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('status','unknown'))" "$state" 2>/dev/null || echo unknown)"
    if [[ "$status" == "paused" ]]; then
      paused+=("$(basename "$(dirname "$state")")")
    fi
  done < <(find "$flows_workflows_dir" -maxdepth 2 -name state.json 2>/dev/null)
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
if [[ ${#paused[@]} -gt 0 ]]; then
  echo "Polymath: ${#paused[@]} paused workflow(s):"
  for w in "${paused[@]}"; do
    echo "  - $w  (resume with /polymath-flows:resume-workflow $w)"
  done
  emitted=1
fi
if [[ -n "$due_now" ]]; then
  [[ $emitted -eq 1 ]] && echo
  echo "Polymath scheduled work due now:"
  printf "%s\n" "$due_now"
fi

exit 0
