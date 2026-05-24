#!/usr/bin/env bash
# Estimate per-plugin always-on listing token cost.
#
# Per-plugin cap (default 400) is the load-bearing gate: each plugin must stay
# under it whether you install 5 or 50. The repo-wide total is informational:
# the script reports it and compares against a *scaling* target of
# (250 × plugin_count), with a floor of 1500 to keep the MVP signal alive.
# Set POLYMATH_MVP_TOTAL_TARGET to override.

set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
plugins_dir="$root/plugins"
per_plugin_ceiling="${POLYMATH_PER_PLUGIN_CEILING:-400}"
plugin_count="$(find "$plugins_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
scaling_target=$(( plugin_count * 250 ))
floor_target=1500
if [[ "$scaling_target" -lt "$floor_target" ]]; then
  scaling_target=$floor_target
fi
total_target="${POLYMATH_MVP_TOTAL_TARGET:-$scaling_target}"

total=0
fail=0

est_chars() {
  python3 - "$1" <<'PY'
import sys, pathlib, re
chars = 0
p = pathlib.Path(sys.argv[1])
for md in p.rglob("*.md"):
    rel = md.relative_to(p)
    parts = rel.parts
    if parts and parts[0] in {"tests", "references"}:
        continue
    if md.name not in {"SKILL.md"} and parts and parts[0] not in {"commands", "agents", "skills"}:
        continue
    text = md.read_text(errors="ignore")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if not m:
        continue
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    desc = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    if name:
        chars += len(name.group(1))
    if desc:
        chars += len(desc.group(1))
print(chars)
PY
}

echo "## Plugin listing budget"
printf "%-30s | %-8s | %s\n" "Plugin" "Tokens" "Status"
printf -- "------------------------------ | -------- | ------\n"

for plugin in "$plugins_dir"/*/; do
  name="$(basename "$plugin")"
  chars="$(est_chars "$plugin" 2>/dev/null || echo 0)"
  tokens=$(( (chars + 3) / 4 ))
  total=$(( total + tokens ))
  status="ok"
  if [[ "$tokens" -gt "$per_plugin_ceiling" ]]; then
    status="OVER ($per_plugin_ceiling)"
    fail=1
  fi
  printf "%-30s | %-8s | %s\n" "$name" "$tokens" "$status"
done

echo
echo "Total measured: $total tokens (target ≤ $total_target)"
if [[ "$total" -gt "$total_target" ]]; then
  echo "FAIL: total exceeds target"
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
