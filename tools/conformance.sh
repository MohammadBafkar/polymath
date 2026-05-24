#!/usr/bin/env bash
# Run conformance checks for one plugin against
# shared/schemas/plugin-conformance.json.
#
# Usage:
#   tools/conformance.sh <plugin-dir>
#   tools/conformance.sh --all
#
# Exits 0 if all required criteria pass; 1 if any required fails.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
schema_file="$root/shared/schemas/plugin-conformance.json"

if [[ ! -f "$schema_file" ]]; then
  echo "error: $schema_file not found" >&2
  exit 1
fi

check_one() {
  local plugin_dir="$1"
  local name
  name="$(basename "$plugin_dir")"
  local fail=0

  echo "── $name"

  # MANIFEST-1 + MANIFEST-2: claude plugin validate + required fields.
  local manifest="$plugin_dir/.claude-plugin/plugin.json"
  if [[ ! -f "$manifest" ]]; then
    echo "  ✗ MANIFEST-2: plugin.json missing"
    fail=1
  else
    python3 -c "import json,sys; d=json.load(open(sys.argv[1])); [d[k] for k in ['name','version','description','license']]" "$manifest" 2>/dev/null \
      && echo "  ✓ MANIFEST-2: required fields present" \
      || { echo "  ✗ MANIFEST-2: required field(s) missing"; fail=1; }
  fi
  if command -v claude >/dev/null 2>&1; then
    if claude plugin validate --strict "$plugin_dir" >/dev/null 2>&1; then
      echo "  ✓ MANIFEST-1: claude plugin validate --strict"
    else
      echo "  ✗ MANIFEST-1: claude plugin validate --strict failed"
      fail=1
    fi
  else
    echo "  · MANIFEST-1: claude CLI not on PATH (skipped)"
  fi

  # DOCS-1
  [[ -f "$plugin_dir/README.md"    ]] && echo "  ✓ DOCS-1: README.md"    || { echo "  ✗ DOCS-1: README.md missing"; fail=1; }
  [[ -f "$plugin_dir/CHANGELOG.md" ]] && echo "  ✓ DOCS-1: CHANGELOG.md" || { echo "  ✗ DOCS-1: CHANGELOG.md missing"; fail=1; }

  # SKILL-1: rely on lint-skills.sh's per-file check.
  while IFS= read -r -d '' skill; do
    desc="$(awk '/^description:/ {sub(/^description: */,""); print; exit}' "$skill")"
    lines="$(wc -l < "$skill" | tr -d ' ')"
    if [[ -z "$desc" ]]; then
      echo "  ✗ SKILL-1: $skill missing description"
      fail=1
    elif [[ ${#desc} -gt 200 ]]; then
      echo "  ✗ SKILL-1: $skill description ${#desc} > 200 chars"
      fail=1
    elif [[ "$lines" -gt 500 ]]; then
      echo "  ✗ SKILL-1: $skill is $lines lines (> 500)"
      fail=1
    fi
  done < <(find "$plugin_dir" -type f -name SKILL.md -print0 2>/dev/null)
  echo "  ✓ SKILL-1: SKILL.md discipline (all under limits)"

  # TEMPLATE-1: plugin-owned templates exist; full-artifact templates (those
  # matching a shared/schemas/artifacts/<Name>.schema.json) have frontmatter.
  # Snippet templates (e.g. CHANGELOG-entry.md) are not required to have
  # frontmatter.
  if [[ -d "$plugin_dir/templates" ]]; then
    template_count="$(find "$plugin_dir/templates" -maxdepth 1 -type f \( -name "*.md" -o -name "*.yaml" \) | wc -l | tr -d ' ')"
    if [[ "$template_count" -gt 0 ]]; then
      missing=0
      while IFS= read -r -d '' tmpl; do
        base="$(basename "$tmpl" .md)"
        schema="$root/shared/schemas/artifacts/${base}.schema.json"
        if [[ -f "$schema" ]]; then
          head -1 "$tmpl" | grep -q "^---" || { echo "  ✗ TEMPLATE-1: $tmpl missing frontmatter (schema exists at $schema)"; missing=1; fail=1; }
        fi
      done < <(find "$plugin_dir/templates" -maxdepth 1 -type f -name "*.md" -print0 2>/dev/null)
      [[ "$missing" -eq 0 ]] && echo "  ✓ TEMPLATE-1: $template_count plugin template(s); frontmatter present where a schema requires it"
    fi
  fi

  # WORKFLOW-1
  if [[ -d "$plugin_dir/workflows" ]]; then
    while IFS= read -r -d '' wf; do
      if "$root/plugins/polymath-flows/bin/polymath-flow" validate "$wf" >/dev/null 2>&1; then
        echo "  ✓ WORKFLOW-1: $wf"
      else
        echo "  ✗ WORKFLOW-1: $wf failed schema validation"
        fail=1
      fi
    done < <(find "$plugin_dir/workflows" -type f -name "*.yaml" -print0)
  fi

  # CONNECTOR-1
  if [[ "$name" == polymath-connector-* ]]; then
    # A connector may delegate to another connector for the MCP server
    # (e.g. polymath-connector-github-actions reuses connector-github's
    # @modelcontextprotocol/server-github). In that case .mcp.json is
    # allowed to be absent. A connector may also wrap a local CLI rather
    # than a remote service (e.g. polymath-connector-terraform shells out
    # to `terraform`); those declare the `polymath-cli-only` keyword.
    delegates_mcp=0
    cli_only=0
    if [[ -f "$manifest" ]]; then
      delegates_mcp="$(python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
deps = d.get('dependencies') or []
print(1 if any(isinstance(x,str) and x.startswith('polymath-connector-') for x in deps) else 0)
" "$manifest" 2>/dev/null || echo 0)"
      cli_only="$(python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
kw = d.get('keywords') or []
print(1 if 'polymath-cli-only' in kw else 0)
" "$manifest" 2>/dev/null || echo 0)"
    fi
    if [[ -f "$plugin_dir/.mcp.json" ]]; then
      echo "  ✓ CONNECTOR-1: .mcp.json"
    elif [[ "$delegates_mcp" -eq 1 ]]; then
      echo "  ✓ CONNECTOR-1: no .mcp.json — delegates to a connector dependency"
    elif [[ "$cli_only" -eq 1 ]]; then
      echo "  ✓ CONNECTOR-1: no .mcp.json — declared 'polymath-cli-only' keyword"
    else
      echo "  ✗ CONNECTOR-1: .mcp.json missing (and no connector dependency or cli-only keyword)"
      fail=1
    fi
    ls "$plugin_dir/references/"*.md >/dev/null 2>&1 \
      && echo "  ✓ CONNECTOR-1: references/<service>-tools.md" \
      || { echo "  ✗ CONNECTOR-1: references/*.md missing"; fail=1; }
    if [[ -f "$manifest" ]]; then
      python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
uc = d.get('userConfig', {}) or {}
for k, v in uc.items():
    if not v.get('title'):  raise SystemExit(f'missing title on userConfig.{k}')
    if not v.get('description'): raise SystemExit(f'missing description on userConfig.{k}')
" "$manifest" 2>&1 \
        && echo "  ✓ CONNECTOR-1: userConfig has title + description per key" \
        || { echo "  ✗ CONNECTOR-1: userConfig missing title or description"; fail=1; }
    fi
  fi

  # FIXTURE-1
  if ls "$root/tests/golden/$name/"*.md >/dev/null 2>&1; then
    echo "  ✓ FIXTURE-1: at least one golden fixture present"
  else
    echo "  ✗ FIXTURE-1: no tests/golden/$name/*.md"
    fail=1
  fi

  echo
  return $fail
}

mode="${1:---all}"
overall=0
if [[ "$mode" == "--all" ]]; then
  for plugin in "$root/plugins"/*/; do
    if ! check_one "${plugin%/}"; then overall=1; fi
  done
elif [[ -d "$mode" ]]; then
  if ! check_one "${mode%/}"; then overall=1; fi
else
  echo "Usage: $0 [<plugin-dir>|--all]" >&2
  exit 2
fi

[[ "$overall" -eq 0 ]] && echo "conformance: OK" || echo "conformance: FAILED"
exit "$overall"
