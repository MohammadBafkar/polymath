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
    # MANIFEST-3: maturity tier (`status`) declared for this plugin in
    # shared/polymath-catalog.json. Lives there rather than in
    # .claude-plugin/marketplace.json because Claude Code's
    # `plugin validate --strict` rejects unknown fields like `status` on
    # plugin entries; the catalog file is Polymath's own schema.
    python3 -c "
import json, sys, pathlib
cat = json.load(open(pathlib.Path(sys.argv[2]).resolve()))
mp = json.load(open(pathlib.Path(sys.argv[3]).resolve()))
name = json.load(open(sys.argv[1])).get('name')
if not any(p.get('name') == name for p in mp.get('plugins', [])):
    raise SystemExit(f'plugin {name!r} not listed in marketplace.json')
entry = cat.get('plugins', {}).get(name)
if entry is None:
    raise SystemExit(f'plugin {name!r} not listed in shared/polymath-catalog.json')
s = entry.get('status')
allowed = {'stable', 'beta', 'experimental', 'deprecated'}
if s not in allowed:
    raise SystemExit(f'status missing or invalid in shared/polymath-catalog.json: {s!r} (allowed: {sorted(allowed)})')
" "$manifest" "$root/shared/polymath-catalog.json" "$root/.claude-plugin/marketplace.json" 2>&1 \
      && echo "  ✓ MANIFEST-3: status declared in shared/polymath-catalog.json (stable / beta / experimental / deprecated)" \
      || { echo "  ✗ MANIFEST-3: status missing or invalid in shared/polymath-catalog.json"; fail=1; }
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

  # CONNECTOR-2: connector / lang / infra plugins must be audited in
  # docs/CONNECTOR-POLICY.md AND must carry the auto-generated
  # disclosure block (official_surface / polymath_value /
  # sunset_trigger / status) in their README, kept in sync via
  # tools/sync-connector-policy.py.
  if [[ "$name" == polymath-connector-* || "$name" == polymath-infra-* ]]; then
    if grep -q "\`$name\`" "$root/docs/CONNECTOR-POLICY.md" 2>/dev/null; then
      echo "  ✓ CONNECTOR-2: audited in docs/CONNECTOR-POLICY.md"
    else
      echo "  ✗ CONNECTOR-2: not audited in docs/CONNECTOR-POLICY.md"
      fail=1
    fi
    if grep -q '<!-- connector-policy:start -->' "$plugin_dir/README.md" 2>/dev/null \
       && grep -q '<!-- connector-policy:end -->' "$plugin_dir/README.md" 2>/dev/null; then
      echo "  ✓ CONNECTOR-2: README carries the policy disclosure block"
    else
      echo "  ✗ CONNECTOR-2: README missing the policy disclosure block (run: python3 tools/sync-connector-policy.py --update)"
      fail=1
    fi
  fi

  # CONNECTOR-1
  if [[ "$name" == polymath-connector-* ]]; then
    # A connector may delegate to another connector for the MCP server
    # via the dependencies array. In that case .mcp.json is allowed to
    # be absent. A connector may also wrap a local CLI rather than a
    # remote service (e.g. polymath-connector-terraform shells out
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
  # Cross-plugin: marketplace.json, every plugin.json, and
  # shared/polymath-catalog.json must agree on the plugin set and on
  # per-plugin versions. Independent of whether the Claude CLI is
  # installed; runs the same check in CI without claude on PATH.
  echo
  echo "── MANIFEST-3 cross-check (check-catalog.py)"
  if python3 "$root/tools/check-catalog.py"; then
    :
  else
    overall=1
  fi

  # Cross-plugin: every in-scope README's connector-policy block must
  # match the policy table verbatim. Local block presence is checked
  # per-plugin above; this catches divergence after a policy-table edit.
  echo
  echo "── CONNECTOR-2 cross-check (sync-connector-policy.py)"
  if python3 "$root/tools/sync-connector-policy.py" --check; then
    :
  else
    overall=1
  fi

  # DOCS-2: every plugin README must mention every shipped first-class
  # surface (skill / command / agent / bin executable) by name. Catches
  # READMEs whose "What it ships" list lags the directory after a new
  # skill / command / scaffolder is added.
  echo
  echo "── DOCS-2 cross-check (check-readme-inventory.py)"
  if python3 "$root/tools/check-readme-inventory.py"; then
    :
  else
    overall=1
  fi

  # STABILITY-1: shared/stability-evidence.json must back every status
  # claim in shared/polymath-catalog.json. The ledger is the receipt for
  # a status flip — a plugin can only be `stable` once the ledger
  # records a live bakeoff, live trigger, external adopter, promotion
  # PR, and changelog entry. Connector/infra plugins additionally need
  # primary-source distinct-value evidence. See docs/MATURITY.md.
  echo
  echo "── STABILITY-1 cross-check (check-stability-evidence.py)"
  if python3 "$root/tools/check-stability-evidence.py"; then
    :
  else
    overall=1
  fi

  # DESC-1: no two always-on descriptions (skill/command/agent) may
  # token-collide without a distinguishing proper noun — a router cannot split
  # them otherwise. Enforces the disambiguation floor; scope_boundary and
  # trigger_clarity are reported but advisory. See tools/lint-descriptions.py.
  echo
  echo "── DESC-1 cross-check (lint-descriptions.py --strict)"
  if python3 "$root/tools/lint-descriptions.py" --strict; then
    :
  else
    overall=1
  fi

  # PROMOTION-1: skill-alias command descriptions must complement, not
  # restate, their target skill (docs/PLUGIN-AUTHORING.md § 5.1). Command
  # descriptions count against the per-plugin token budget, so a verbatim
  # shim spends budget for zero added discoverability.
  echo
  echo "── PROMOTION-1 cross-check (check-command-overlap.py)"
  if python3 "$root/tools/check-command-overlap.py"; then
    :
  else
    overall=1
  fi

  # PROMOTION-2: every workflow step's `invoke: plugin:skill` must resolve
  # to a real SKILL.md. Catches a workflow left pointing at a renamed or
  # removed skill — no other gate checks this.
  echo
  echo "── PROMOTION-2 cross-check (check-workflow-invokes.py)"
  if python3 "$root/tools/check-workflow-invokes.py"; then
    :
  else
    overall=1
  fi

  # WORKFLOW-INDEX: the committed workflow routing index
  # (plugins/polymath-flows/data/*.json) must match a fresh build from the
  # workflow YAML `whenToUse`/`triggers`/`detectionSignals`. The index is the
  # SessionStart routing surface; this diff-guard keeps it from drifting and
  # asserts the injected min-index stays under its token ceiling.
  echo
  echo "── WORKFLOW-INDEX cross-check (build-workflow-index.py --check --strict)"
  if python3 "$root/tools/build-workflow-index.py" --check --strict; then
    :
  else
    overall=1
  fi

  # WORKFLOW-TRIGGER: workflow-triggering test frontmatter is well-formed and in
  # sync with the workflow YAML (every declared trigger appears in its test, and
  # must_propose names resolve). Cheap structural check, no LLM; the live `run`
  # mode is a separate opt-in CI job under CLAUDE_CODE_OAUTH_TOKEN.
  echo
  echo "── WORKFLOW-TRIGGER cross-check (workflow-triggering.py check)"
  if python3 "$root/tools/workflow-triggering.py" check; then
    :
  else
    overall=1
  fi
elif [[ -d "$mode" ]]; then
  if ! check_one "${mode%/}"; then overall=1; fi
else
  echo "Usage: $0 [<plugin-dir>|--all]" >&2
  exit 2
fi

[[ "$overall" -eq 0 ]] && echo "conformance: OK" || echo "conformance: FAILED"
exit "$overall"
