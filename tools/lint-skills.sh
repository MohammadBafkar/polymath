#!/usr/bin/env bash
# Enforce skill/command frontmatter discipline:
#   - description field present and ≤ 200 chars
#   - SKILL.md ≤ 500 lines
#   - description starts with an imperative verb-ish lowercase letter (advisory)
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
plugins_dir="$root/plugins"
fail=0

check_file() {
  local file="$1"
  local kind="$2"  # SKILL or COMMAND
  local frontmatter
  frontmatter="$(awk '/^---$/{c++; next} c==1{print} c==2{exit}' "$file")"
  if [[ -z "$frontmatter" ]]; then
    echo "✗ $file: no frontmatter"
    return 1
  fi
  local desc
  desc="$(echo "$frontmatter" | awk '/^description:/ {sub(/^description: */,""); print; exit}')"
  if [[ -z "$desc" ]]; then
    echo "✗ $file: missing description"
    return 1
  fi
  if [[ ${#desc} -gt 200 ]]; then
    echo "✗ $file: description is ${#desc} chars (> 200)"
    return 1
  fi
  if [[ "$kind" == "SKILL" ]]; then
    local lines
    lines="$(wc -l < "$file" | tr -d ' ')"
    if [[ "$lines" -gt 500 ]]; then
      echo "✗ $file: $lines lines (> 500)"
      return 1
    fi
  fi
  return 0
}

while IFS= read -r -d '' f; do
  check_file "$f" SKILL || fail=1
done < <(find "$plugins_dir" -type f -name SKILL.md -print0 2>/dev/null)

while IFS= read -r -d '' f; do
  # commands directly under plugins/<plugin>/commands/
  case "$f" in
    */commands/*.md) check_file "$f" COMMAND || fail=1 ;;
  esac
done < <(find "$plugins_dir" -type f -path "*/commands/*.md" -print0 2>/dev/null)

# Output-shape ratchet: a SKILL.md's `## Output` section should show the exact
# shape it produces (a fenced example, a templates/ link, a *.schema.json ref,
# or a docs/<area> path) so the model has something to imitate. Existing
# shapeless skills are grandfathered in the baseline; this fails on any NEW
# shapeless skill and on any baselined skill that has since gained a shape
# (remove it — the baseline only shrinks).
baseline_file="$root/registry/output-shape-baseline.txt"
if [[ -f "$baseline_file" ]]; then
  current="$(mktemp)"; baseline_sorted="$(mktemp)"
  while IFS= read -r -d '' f; do
    awk '
      /^##[[:space:]]/        { in_out = ($0 ~ /[Oo]utput/) ? 1 : 0; next }
      in_out && /```/         { found=1 }
      in_out && /templates\// { found=1 }
      in_out && /\.schema\.json/ { found=1 }
      in_out && /docs\/[a-z]/ { found=1 }
      END { exit (found ? 0 : 1) }
    ' "$f" || echo "$f" | sed -E 's#.*/plugins/([^/]+)/skills/([^/]+)/SKILL.md#\1:\2#'
  done < <(find "$plugins_dir" -type f -name SKILL.md -print0) | sort > "$current"
  grep -vE '^[[:space:]]*(#|$)' "$baseline_file" | sort > "$baseline_sorted"
  new_viol="$(comm -23 "$current" "$baseline_sorted")"
  fixed="$(comm -13 "$current" "$baseline_sorted")"
  if [[ -n "$new_viol" ]]; then
    echo "✗ output-shape: these skills' '## Output' section shows no shape (add a fenced example, a templates/ link, a *.schema.json ref, or a docs/<area> path):"
    echo "$new_viol" | sed 's/^/    /'
    fail=1
  fi
  if [[ -n "$fixed" ]]; then
    echo "✗ output-shape: these baselined skills now show a shape — delete them from registry/output-shape-baseline.txt (the baseline only shrinks):"
    echo "$fixed" | sed 's/^/    /'
    fail=1
  fi
  rm -f "$current" "$baseline_sorted"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "lint-skills: FAILED"
  exit 1
fi
echo "lint-skills: OK"
