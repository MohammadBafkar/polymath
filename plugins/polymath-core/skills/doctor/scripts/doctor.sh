#!/usr/bin/env bash
# polymath-core:doctor — preflight environment check.
#
# Reports PASS / WARN / FAIL for the tools Polymath relies on, plus the
# validity of any .polymath/project.yaml in the current repo. Exits non-zero
# only when a REQUIRED tool is missing, so it can gate init-project as step 0.
#
# Required:    bash, python3
# Recommended: git (workflows + first-run nudge), claude CLI (strict validate,
#              live golden fixtures)
# Optional:    PyYAML (the loader has a hand-rolled fallback), jq
set -uo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
loader="${script_dir}/../../../hooks/scripts/load-project-context.py"

req_fail=0
pass() { printf '  ✓ %-10s %s\n' "$1" "$2"; }
warn() { printf '  ! %-10s %s\n' "$1" "$2"; }
fail() { printf '  ✗ %-10s %s\n' "$1" "$2"; }

echo "polymath-core:doctor — environment preflight"
echo
echo "Required:"
if command -v bash >/dev/null 2>&1; then
  pass "bash" "$(bash --version 2>/dev/null | head -1)"
else
  fail "bash" "not found — install bash"; req_fail=1
fi
if command -v python3 >/dev/null 2>&1; then
  pass "python3" "$(python3 --version 2>&1)"
else
  fail "python3" "not found — install Python 3 (hooks, loader, and tools need it)"; req_fail=1
fi

echo
echo "Recommended:"
if command -v git >/dev/null 2>&1; then
  pass "git" "$(git --version 2>&1)"
else
  warn "git" "not found — workflows and the first-run nudge need a git repo"
fi
if command -v claude >/dev/null 2>&1; then
  pass "claude" "$(claude --version 2>&1 | head -1)"
else
  warn "claude" "not found — needed for 'claude plugin validate --strict' and live golden fixtures"
fi

echo
echo "Optional:"
if command -v python3 >/dev/null 2>&1 && python3 -c "import yaml" >/dev/null 2>&1; then
  pass "PyYAML" "present (richer project.yaml parsing)"
else
  warn "PyYAML" "absent — the loader falls back to a minimal parser; fine for simple files"
fi
if command -v jq >/dev/null 2>&1; then
  pass "jq" "$(jq --version 2>&1)"
else
  warn "jq" "absent — not required by Polymath; handy for inspecting JSON snapshots"
fi

echo
echo "Project context:"
if [[ -f ".polymath/project.yaml" ]]; then
  if command -v python3 >/dev/null 2>&1 && [[ -x "$loader" ]]; then
    tmp_data="$(mktemp -d)"
    if out="$(CLAUDE_PLUGIN_DATA="$tmp_data" python3 "$loader" 2>&1)"; then
      pass "project.yaml" "valid — ${out#Polymath: }"
    else
      fail "project.yaml" "present but the loader rejected it:"
      printf '%s\n' "$out" | sed 's/^/      /'
      # A bad project file is a real problem, but not a missing-tool failure;
      # surface it without failing the required-tools gate.
    fi
    rm -rf "$tmp_data"
  else
    warn "project.yaml" "present (cannot validate — python3 or loader unavailable)"
  fi
else
  warn "project.yaml" "not found — run /polymath-core:init-project to create it"
fi

echo
if [[ "$req_fail" -ne 0 ]]; then
  echo "doctor: FAILED — a required tool is missing (see ✗ above)."
  exit 1
fi
echo "doctor: OK — required tools present."
exit 0
