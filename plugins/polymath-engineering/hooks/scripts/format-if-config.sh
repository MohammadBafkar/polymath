#!/usr/bin/env bash
# polymath-engineering PostToolUse(Write|Edit) hook
#
# Runs the project formatter on the just-edited file ONLY if a matching formatter
# config exists in the project. No-op otherwise. Never modifies a file in-place
# without a config — that would be a surprise.
#
# Reads the tool-input payload from stdin and uses the `file_path` field.
set -euo pipefail

payload="$(cat)"

file="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    args = data.get("tool_input", {}) or {}
    print(args.get("file_path", ""))
except Exception:
    pass
' 2>/dev/null || true)"

if [[ -z "$file" || ! -f "$file" ]]; then
  exit 0
fi

# Walk up from file looking for config markers + matching binaries.
dir="$(dirname "$file")"
project_root=""
while [[ "$dir" != "/" && "$dir" != "." ]]; do
  if [[ -f "$dir/.git/HEAD" || -f "$dir/package.json" || -f "$dir/pyproject.toml" || -f "$dir/Cargo.toml" || -f "$dir/go.mod" ]]; then
    project_root="$dir"
    break
  fi
  dir="$(dirname "$dir")"
done

[[ -z "$project_root" ]] && exit 0

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.md|*.css|*.scss)
    if [[ -f "$project_root/biome.json" || -f "$project_root/.biome.json" ]] && command -v biome >/dev/null 2>&1; then
      biome format --write "$file" 2>/dev/null || true
      echo "polymath-engineering: biome formatted $file"
    elif [[ -f "$project_root/.prettierrc"* ]] && command -v prettier >/dev/null 2>&1; then
      prettier --write "$file" 2>/dev/null || true
      echo "polymath-engineering: prettier formatted $file"
    fi
    ;;
  *.py)
    if [[ -f "$project_root/pyproject.toml" ]] && grep -q "ruff" "$project_root/pyproject.toml" 2>/dev/null && command -v ruff >/dev/null 2>&1; then
      ruff format "$file" 2>/dev/null || true
      echo "polymath-engineering: ruff formatted $file"
    fi
    ;;
  *.rs)
    if [[ -f "$project_root/rustfmt.toml" || -f "$project_root/.rustfmt.toml" ]] && command -v rustfmt >/dev/null 2>&1; then
      rustfmt "$file" 2>/dev/null || true
      echo "polymath-engineering: rustfmt formatted $file"
    fi
    ;;
  *.go)
    if command -v gofmt >/dev/null 2>&1; then
      gofmt -w "$file" 2>/dev/null || true
      echo "polymath-engineering: gofmt formatted $file"
    fi
    ;;
esac

exit 0
