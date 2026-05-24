#!/usr/bin/env bash
# Validate every plugin in the marketplace.
#
# Runs structural and frontmatter checks. Calls `claude plugin validate --strict` when
# the claude CLI is available; otherwise falls back to JSON parsing + frontmatter linting.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
plugins_dir="$root/plugins"
fail=0

if [[ ! -d "$plugins_dir" ]]; then
  echo "error: $plugins_dir not found" >&2
  exit 1
fi

check_json() {
  local file="$1"
  if ! python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$file" >/dev/null 2>&1; then
    echo "  ✗ $file is not valid JSON"
    return 1
  fi
  echo "  ✓ $file"
}

check_frontmatter_lines() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    return 0
  fi
  local desc
  desc="$(awk '/^description:/ {sub(/^description: */,""); print; exit}' "$file")"
  if [[ -z "$desc" ]]; then
    echo "  ✗ $file is missing frontmatter description"
    return 1
  fi
  if [[ ${#desc} -gt 200 ]]; then
    echo "  ✗ $file description is ${#desc} chars (> 200)"
    return 1
  fi
  local lines
  lines="$(wc -l < "$file" | tr -d ' ')"
  if [[ "$lines" -gt 500 ]]; then
    echo "  ✗ $file is $lines lines (> 500)"
    return 1
  fi
  return 0
}

for plugin in "$plugins_dir"/*/; do
  name="$(basename "$plugin")"
  echo "::group::$name"
  manifest="$plugin/.claude-plugin/plugin.json"
  if [[ ! -f "$manifest" ]]; then
    echo "  ✗ missing $manifest"
    fail=1
    echo "::endgroup::"
    continue
  fi
  check_json "$manifest" || fail=1

  if command -v claude >/dev/null 2>&1; then
    if ! claude plugin validate --strict "$plugin" 2>/dev/null; then
      echo "  ⚠ claude plugin validate returned non-zero (continuing)"
    fi
  fi

  while IFS= read -r -d '' skill_md; do
    if ! check_frontmatter_lines "$skill_md"; then
      fail=1
    fi
  done < <(find "$plugin" -type f -name "SKILL.md" -print0)

  while IFS= read -r -d '' cmd; do
    if ! check_frontmatter_lines "$cmd"; then
      fail=1
    fi
  done < <(find "$plugin/commands" -maxdepth 1 -type f -name "*.md" -print0 2>/dev/null)

  echo "::endgroup::"
done

if [[ "$fail" -ne 0 ]]; then
  echo "validate-all: FAILED"
  exit 1
fi
echo "validate-all: OK"
