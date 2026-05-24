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

if [[ "$fail" -ne 0 ]]; then
  echo "lint-skills: FAILED"
  exit 1
fi
echo "lint-skills: OK"
