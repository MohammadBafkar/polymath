#!/usr/bin/env bash
# Run conformance checks for one plugin against
# registry/schemas/plugin-conformance.json.
#
# Usage:
#   tools/conformance.sh <plugin-dir>
#   tools/conformance.sh --all
#
# Exits 0 if all required criteria pass; 1 if any required fails.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
schema_file="$root/registry/schemas/plugin-conformance.json"

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
    # registry/polymath-catalog.json. Lives there rather than in
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
    raise SystemExit(f'plugin {name!r} not listed in registry/polymath-catalog.json')
s = entry.get('status')
allowed = {'stable', 'beta', 'experimental', 'deprecated'}
if s not in allowed:
    raise SystemExit(f'status missing or invalid in registry/polymath-catalog.json: {s!r} (allowed: {sorted(allowed)})')
" "$manifest" "$root/registry/polymath-catalog.json" "$root/.claude-plugin/marketplace.json" 2>&1 \
      && echo "  ✓ MANIFEST-3: status declared in registry/polymath-catalog.json (stable / beta / experimental / deprecated)" \
      || { echo "  ✗ MANIFEST-3: status missing or invalid in registry/polymath-catalog.json"; fail=1; }
  fi
  if command -v claude >/dev/null 2>&1; then
    if claude plugin validate --strict "$plugin_dir" >/dev/null 2>&1; then
      echo "  ✓ MANIFEST-1: claude plugin validate --strict"
    else
      echo "  ✗ MANIFEST-1: claude plugin validate --strict failed"
      fail=1
    fi
  elif [[ -n "${CI:-}" ]]; then
    # A silent CI skip is how MANIFEST-1 ran zero times while looking green.
    echo "  ✗ MANIFEST-1: claude CLI not on PATH in CI (validate.yml installs a pinned version)"
    fail=1
  else
    echo "  · MANIFEST-1: claude CLI not on PATH (skipped locally)"
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
  # matching a registry/schemas/artifacts/<Name>.schema.json) have frontmatter.
  # Snippet templates (e.g. CHANGELOG-entry.md) are not required to have
  # frontmatter.
  if [[ -d "$plugin_dir/templates" ]]; then
    template_count="$(find "$plugin_dir/templates" -maxdepth 1 -type f \( -name "*.md" -o -name "*.yaml" \) | wc -l | tr -d ' ')"
    if [[ "$template_count" -gt 0 ]]; then
      missing=0
      while IFS= read -r -d '' tmpl; do
        base="$(basename "$tmpl" .md)"
        schema="$root/registry/schemas/artifacts/${base}.schema.json"
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

  # INTEGRATION-2: connector / lang / infra plugins must be audited in
  # docs/INTEGRATION-POLICY.md AND must carry the auto-generated
  # disclosure block (official_surface / polymath_value /
  # sunset_trigger / status) in their README, kept in sync via
  # tools/sync-integration-policy.py.
  # Detect policy-scoped plugins by artifact, not name prefix, so concept-plugin
  # renames (vcs / chat / paging / cloud / kubernetes …) and the observability
  # merge stay covered. An MCP connector ships a .mcp.json; an infra plugin
  # carries capability bindings/ but no .mcp.json. INTEGRATION-2 (policy
  # disclosure) covers both; INTEGRATION-1 (.mcp.json/references/userConfig)
  # covers MCP connectors only.
  is_connector=0
  [[ -f "$plugin_dir/.mcp.json" ]] && is_connector=1
  is_policy_scoped=0
  [[ -f "$plugin_dir/.mcp.json" || -d "$plugin_dir/bindings" ]] && is_policy_scoped=1
  if [[ "$is_policy_scoped" -eq 1 ]]; then
    if grep -q "\`$name\`" "$root/docs/INTEGRATION-POLICY.md" 2>/dev/null; then
      echo "  ✓ INTEGRATION-2: audited in docs/INTEGRATION-POLICY.md"
    else
      echo "  ✗ INTEGRATION-2: not audited in docs/INTEGRATION-POLICY.md"
      fail=1
    fi
    if grep -q '<!-- integration-policy:start -->' "$plugin_dir/README.md" 2>/dev/null \
       && grep -q '<!-- integration-policy:end -->' "$plugin_dir/README.md" 2>/dev/null; then
      echo "  ✓ INTEGRATION-2: README carries the policy disclosure block"
    else
      echo "  ✗ INTEGRATION-2: README missing the policy disclosure block (run: python3 tools/sync-integration-policy.py --update)"
      fail=1
    fi
  fi

  # INTEGRATION-1 — applies to MCP connectors (ship a .mcp.json), detected by
  # artifact rather than name prefix.
  if [[ "$is_connector" -eq 1 ]]; then
    # is_connector ⟺ a .mcp.json is present (detected above). An integration
    # plugin must also ship references/<service>-tools.md and userConfig with
    # title + description per key.
    echo "  ✓ INTEGRATION-1: .mcp.json"
    ls "$plugin_dir/references/"*.md >/dev/null 2>&1 \
      && echo "  ✓ INTEGRATION-1: references/<service>-tools.md" \
      || { echo "  ✗ INTEGRATION-1: references/*.md missing"; fail=1; }
    if [[ -f "$manifest" ]]; then
      python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
uc = d.get('userConfig', {}) or {}
for k, v in uc.items():
    if not v.get('title'):  raise SystemExit(f'missing title on userConfig.{k}')
    if not v.get('description'): raise SystemExit(f'missing description on userConfig.{k}')
" "$manifest" 2>&1 \
        && echo "  ✓ INTEGRATION-1: userConfig has title + description per key" \
        || { echo "  ✗ INTEGRATION-1: userConfig missing title or description"; fail=1; }
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
  # registry/polymath-catalog.json must agree on the plugin set and on
  # per-plugin versions. Independent of whether the Claude CLI is
  # installed; runs the same check in CI without claude on PATH.
  echo
  echo "── MANIFEST-3 cross-check (check-registry.py catalog)"
  if python3 "$root/tools/check-registry.py" catalog; then
    :
  else
    overall=1
  fi

  # Cross-plugin: every in-scope README's integration-policy block must
  # match the policy table verbatim. Local block presence is checked
  # per-plugin above; this catches divergence after a policy-table edit.
  echo
  echo "── INTEGRATION-2 cross-check (sync-integration-policy.py)"
  if python3 "$root/tools/sync-integration-policy.py" --check; then
    :
  else
    overall=1
  fi

  # MCP-PKG: every connector .mcp.json package is either confirmed to
  # resolve on npm or explicitly disclosed as a placeholder in its README.
  # Prevents a dead-on-install connector (npx -y <missing> never starts)
  # from shipping silently. Offline/hermetic; see tools/check-mcp-packages.py.
  echo
  echo "── MCP-PKG cross-check (check-mcp-packages.py)"
  if python3 "$root/tools/check-mcp-packages.py"; then
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

  # STABILITY-1: registry/stability-evidence.json must back every status
  # claim in registry/polymath-catalog.json. The ledger is the receipt for
  # a status flip — a plugin can only be `stable` once the ledger
  # records a live bakeoff, live trigger, external adopter, promotion
  # PR, and changelog entry. Connector/infra plugins additionally need
  # primary-source distinct-value evidence. See docs/MATURITY.md.
  echo
  echo "── STABILITY-1 cross-check (check-registry.py stability)"
  if python3 "$root/tools/check-registry.py" stability; then
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

  # DESC-2: confusion-matrix frontmatter is well-formed (referenced skills
  # exist). The behavioural assertion — naive prompt loads the expected skill,
  # never a forbidden sibling — is the opt-in `run` mode under
  # CLAUDE_CODE_OAUTH_TOKEN. See tools/check-description-confusion.py.
  echo
  echo "── DESC-2 cross-check (check-description-confusion.py check)"
  if python3 "$root/tools/check-description-confusion.py" check; then
    :
  else
    overall=1
  fi

  # AGENT-1: every plugin agent ships a baseline-beating golden fixture and
  # does not compete with a workflow on intent (docs/PLUGIN-AUTHORING.md §6 /
  # §6.1). Blocks the role-as-agent anti-pattern from regressing silently.
  echo
  echo "── AGENT-1 cross-check (check-agents.py)"
  if python3 "$root/tools/check-agents.py"; then
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

  # SURFACE-INDEX: the deterministic route table (plugins/polymath-core/data/
  # route-signals.json) and the surface catalog (surface-index.json) must match
  # a fresh build from the per-surface routing.yaml sidecars (skills + workflows
  # + tools). tools/build-surface-index.py is the SINGLE PRODUCER; route-signals
  # is no longer hand-maintained. --strict additionally enforces SURFACE-2:
  # every intent / url / regex pattern is globally unique (the disambiguation
  # floor extended from workflows to all surfaces).
  echo
  echo "── SURFACE-INDEX cross-check (build-surface-index.py --check --strict)"
  if python3 "$root/tools/build-surface-index.py" --check --strict; then
    :
  else
    overall=1
  fi

  # CAPABILITY-INDEX + BINDING-1 are ONE gate run by ONE command
  # (build-capability-index.py --check --strict): --check is the drift guard on
  # registry/schemas/capabilities.json `providerPlugins{}` (the SINGLE PRODUCER
  # builds it from the per-provider bindings plugins/<plugin>/bindings/<provider>/
  # binding.json, so a provider is wired iff a binding exists), and --strict
  # (BINDING-1) requires every binding's provider to appear in its capability's
  # providers[] vocabulary and forbids two plugins claiming the same (capability,
  # provider). The precomputed `providerPlugins{}` map is RETAINED (not resolved
  # lazily) because bin/polymath-flow reads it at runtime for O(1) capability →
  # plugin resolution.
  echo
  echo "── CAPABILITY-INDEX + BINDING-1 cross-check (build-capability-index.py --check --strict)"
  if python3 "$root/tools/build-capability-index.py" --check --strict; then
    :
  else
    overall=1
  fi

  # WORKFLOW-TRIGGER: workflow-triggering test frontmatter is well-formed and in
  # sync with the workflow YAML (every declared trigger appears in its test, and
  # must_propose names resolve). Cheap structural check, no LLM; the live `run`
  # mode is a separate opt-in CI job under CLAUDE_CODE_OAUTH_TOKEN.
  echo
  echo "── WORKFLOW-TRIGGER cross-check (triggering.py workflow check)"
  if python3 "$root/tools/triggering.py" workflow check; then
    :
  else
    overall=1
  fi

  # ROUTE-TRIGGER: the ambient routing hint hook (polymath-core route-hint) is a
  # deterministic function of the prompt text, so unlike skill/workflow triggering
  # this is run live here — no model, no token, no opt-in. A regression in the
  # signal table or the scorer fails the build.
  echo
  echo "── ROUTE-TRIGGER cross-check (triggering.py route run)"
  if python3 "$root/tools/triggering.py" route run; then
    :
  else
    overall=1
  fi

  # COUNT-1 / TESTDIR-1 / DOCPATH-1: drift gates. README aggregate counts are
  # marker-wrapped and recomputed from the tree; fixture dirs must name real
  # plugins; relative doc links must resolve. Each has a --self-test proving
  # it can fail.
  for sub in aggregates testdirs docpaths; do
    echo
    echo "── ${sub} cross-check (check-registry.py ${sub})"
    if python3 "$root/tools/check-registry.py" "$sub"; then
      :
    else
      overall=1
    fi
  done

  # GATES-1: registry/gates.json is the machine-readable source of truth for
  # gate IDs — bijective with the IDs in this script, and every entry marked
  # verification=selftest has its registered --self-test executed here.
  echo
  echo "── GATES-1 cross-check (check-registry.py gates)"
  if python3 "$root/tools/check-registry.py" gates; then
    :
  else
    overall=1
  fi

  # ROUTE-EVAL-1: the held-out routing eval's two invariants — token precision
  # 1.0 and zero false positives — gate the build; reach is reported, never
  # floored. Also drift-guards the committed route-metrics.json against a
  # fresh computation. Deterministic: no model, no token.
  echo
  echo "── ROUTE-EVAL-1 cross-check (triggering.py route-eval --gate)"
  if python3 "$root/tools/triggering.py" route-eval --gate >/dev/null 2>&1; then
    echo "route-eval gate: OK (precision 1.0, false positives 0; metrics file in sync)"
  else
    python3 "$root/tools/triggering.py" route-eval --gate | tail -8
    overall=1
  fi

  # PROFILE-1: install profiles (registry/polymath-profiles.json) only name
  # plugins that exist in the marketplace. Drift-guard so a fold/rename can't
  # leave a dangling profile reference.
  echo
  echo "── PROFILE-1 cross-check (check-registry.py profiles)"
  if python3 "$root/tools/check-registry.py" profiles; then
    :
  else
    overall=1
  fi

  # PROFILE-2: each install profile's summed always-on listing cost stays
  # within its declared alwaysOnBudget (registry/polymath-profiles.json).
  echo
  echo "── PROFILE-2 cross-check (token-report.py profiles)"
  if python3 "$root/tools/token-report.py" profiles; then
    :
  else
    overall=1
  fi

  # SURFACE-1: every catalog surface either declares routing or carries an
  # exemption with a reason; the hard tier only ratchets up and every
  # hard-tier surface is fixture-backed.
  echo
  echo "── SURFACE-1 cross-check (check-registry.py routing)"
  if python3 "$root/tools/check-registry.py" routing; then
    :
  else
    overall=1
  fi

  # CONFUSION-1: shortlist ties over the held-out corpus. Sub-threshold
  # ties are advisory; a tie where BOTH candidates clear the ambient
  # firing bar fails (the hint itself would be ambiguous).
  echo
  echo "── CONFUSION-1 cross-check (triggering.py confusion --gate)"
  if python3 "$root/tools/triggering.py" confusion --gate >/dev/null 2>&1; then
    echo "confusion gate: OK (no firing ties on the corpus)"
  else
    python3 "$root/tools/triggering.py" confusion --gate | tail -6
    overall=1
  fi

  # HINT-BUDGET: the worst single-candidate ambient route hint must stay
  # within its token budget (template bloat or a verbose surface fails).
  echo
  echo "── HINT-BUDGET cross-check (build-surface-index.py --hint-budget)"
  if python3 "$root/tools/build-surface-index.py" --hint-budget; then
    :
  else
    overall=1
  fi

  # DEADCONF-1: every project.schema.json property (top-level + named children)
  # is read by a real consumer — a skill contract, hook, Python runner, or tool
  # — or is listed in registry/deadconfig-exemptions.json with a reason.
  # Admission into KNOWN_TOP_KEYS, shape/enum validation in the loader, and *.sh
  # scaffolders that merely emit keys do NOT count as consumers.
  echo
  echo "── DEADCONF-1 cross-check (check-registry.py deadconfig)"
  if python3 "$root/tools/check-registry.py" deadconfig; then
    :
  else
    overall=1
  fi

  # COUPLING-1: catalog-wide Claude-coupling occurrences must not exceed the
  # frozen ceiling (registry/coupling-baseline.json) — coupling may shrink but
  # never grow silently. Per-occurrence enumeration (which skill, which line)
  # is a separate, deferred gate.
  echo
  echo "── COUPLING-1 cross-check (export-agents-skills.py --coupling-ratchet)"
  if python3 "$root/tools/export-agents-skills.py" --coupling-ratchet; then
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
