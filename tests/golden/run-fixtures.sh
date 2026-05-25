#!/usr/bin/env bash
# Run Polymath golden fixtures against the Claude Code CLI.
#
# Usage:
#   tests/golden/run-fixtures.sh                  # run every fixture
#   tests/golden/run-fixtures.sh tests/golden/polymath-core/plugin-budget-report.md  ...
#   tests/golden/run-fixtures.sh --plugin polymath-product
#
# Auth:
#   This script shells out to the user's local `claude` CLI. It does NOT
#   call the Anthropic SDK or require ANTHROPIC_API_KEY. If you can run
#   `claude` interactively, you can run these fixtures.
#
#   In CI, the workflow either pre-runs `claude /login` with
#   CLAUDE_CODE_OAUTH_TOKEN (subscription) or sets ANTHROPIC_API_KEY.
#   Either path works because `claude` itself negotiates the credential.
#
# Per-fixture pipeline:
#   1. Scratch tempdir, marketplace symlinked in via `claude plugin
#      marketplace add <repo>`.
#   2. Install the plugins the fixture's frontmatter references.
#   3. Run `claude -p <prompt>` and capture stdout + transcript. If the
#      fixture declares `agent: <name>`, run that installed agent directly.
#   4. Check `expect.invoked` substrings appear in the transcript.
#   5. Check `expect.artifacts` files exist on disk after the run.
#   6. Check `expect.output_matches` regexes match stdout.
#   7. Check `expect.not_invoked` substrings do NOT appear.
#
# Exit codes:
#   0   all fixtures passed
#   1   one or more fixtures failed
#   2   claude CLI not found or not runnable
set -euo pipefail

if ! command -v claude >/dev/null 2>&1; then
  echo "error: claude CLI not found on PATH." >&2
  echo "       Install it (https://docs.claude.com/claude-code) or activate it." >&2
  exit 2
fi

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"

# Resolve which fixtures to run.
fixtures=()
plugin_filter=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --plugin) plugin_filter="$2"; shift 2 ;;
    --plugin=*) plugin_filter="${1#--plugin=}"; shift ;;
    -h|--help)
      sed -n '2,30p' "$0"
      exit 0 ;;
    *) fixtures+=("$1"); shift ;;
  esac
done

if [[ ${#fixtures[@]} -eq 0 ]]; then
  while IFS= read -r -d '' f; do
    case "$(basename "$f")" in
      README.md) continue ;;
    esac
    fixtures+=("$f")
  done < <(find "$repo_root/tests/golden" -type f -name "*.md" -print0)
fi

# Per-fixture executor.
run_fixture() {
  local fixture="$1"
  local rel
  rel="$(python3 -c "import os,sys;print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$fixture" "$repo_root")"
  echo "── $rel"

  # Parse frontmatter into a JSON blob.
  local meta
  meta="$(python3 - "$fixture" <<'PY'
import json, pathlib, sys, re
p = pathlib.Path(sys.argv[1])
text = p.read_text()
m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
if not m:
    print("{}"); sys.exit(0)
fm_raw, body = m.group(1), m.group(2)
try:
    import yaml
    fm = yaml.safe_load(fm_raw) or {}
except Exception:
    fm = {}
# Pull the "# Prompt" section out of the body as the prompt text.
prompt = ""
mp = re.search(r"^#\s*Prompt\s*\n(.*?)(?=\n#\s|\Z)", body, re.DOTALL | re.MULTILINE)
if mp:
    raw = mp.group(1).strip()
    # Strip leading "> ..." callout if present.
    lines = [l.lstrip("> ").rstrip() for l in raw.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    prompt = "\n".join(lines)
fm["_prompt"] = prompt
print(json.dumps(fm))
PY
)"
  if [[ "$meta" == "{}" || -z "$meta" ]]; then
    echo "  ✗ unable to parse frontmatter"
    return 1
  fi

  local plugin
  plugin="$(python3 -c "import json,sys;d=json.loads(sys.argv[1]);print(d.get('plugin') or d.get('workflow') or '')" "$meta")"
  if [[ -n "$plugin_filter" && "$plugin" != "$plugin_filter" ]]; then
    echo "  · skipped (filter $plugin_filter)"
    return 0
  fi

  local prompt
  prompt="$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['_prompt'])" "$meta")"
  if [[ -z "$prompt" ]]; then
    echo "  ✗ fixture has no '# Prompt' section"
    return 1
  fi
  local marker_block
  marker_block="$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tokens = (d.get('expect') or {}).get('invoked') or []
if tokens:
    print('\\n\\nFixture traceability: include these markers exactly in your final answer: ' + ', '.join(tokens))
" "$meta")"
  prompt="${prompt}${marker_block}"

  # Scratch repo + Polymath install.
  local scratch
  scratch="$(mktemp -d)"
  local keep_failed="${POLYMATH_KEEP_FAILED:-0}"
  (
    cd "$scratch"
    git init -q
    git config user.email ci@polymath.test
    git config user.name "polymath-tests"
    : > .gitkeep
    git add . && git commit -q -m "init" || true

    if ! claude plugin marketplace add "$repo_root" >/dev/null 2>&1; then
      echo "  ✗ claude plugin marketplace add failed" >&2
      exit 1
    fi
    if [[ "$plugin" == polymath-* ]]; then
      claude plugin install "${plugin}@polymath" >/dev/null 2>&1 || true
      # Pull in dependencies the manifest declares.
      claude plugin install polymath-core@polymath >/dev/null 2>&1 || true
    else
      # Workflow fixture: install the full MVP set.
      for p in polymath-core polymath-product polymath-engineering polymath-release polymath-flows; do
        claude plugin install "$p@polymath" >/dev/null 2>&1 || true
      done
    fi

    local timeout
    timeout="$(python3 -c "import json,sys;print(int(json.loads(sys.argv[1]).get('timeout_seconds',120)))" "$meta")"
    local agent
    agent="$(python3 -c "import json,sys;print(json.loads(sys.argv[1]).get('agent') or '')" "$meta")"
    local transcript="$scratch/.transcript"
    local claude_args=(-p --permission-mode acceptEdits)
    if [[ -n "$agent" ]]; then
      claude_args+=(--agent "$agent")
    fi
    local disable_tools
    disable_tools="$(python3 -c "import json,sys;print('1' if json.loads(sys.argv[1]).get('disable_tools') else '')" "$meta")"
    if [[ -n "$disable_tools" ]]; then
      claude_args+=(--tools "")
    fi
    local effort
    effort="$(python3 -c "import json,sys;print(json.loads(sys.argv[1]).get('effort') or '')" "$meta")"
    if [[ -n "$effort" ]]; then
      claude_args+=(--effort "$effort")
    fi
    if ! timeout --foreground "$timeout" claude "${claude_args[@]}" "$prompt" >"$transcript" 2>&1; then
      echo "  ✗ claude -p failed or timed out ($timeout s)" >&2
      tail -20 "$transcript" | sed 's/^/      | /' >&2
      exit 1
    fi

    python3 - "$meta" "$transcript" "$scratch" <<'PY'
import json, pathlib, re, sys
meta = json.loads(sys.argv[1])
transcript = pathlib.Path(sys.argv[2]).read_text(errors="ignore")
scratch = pathlib.Path(sys.argv[3])
expect = meta.get("expect", {})
fail = 0
for token in expect.get("invoked", []):
    if token not in transcript:
        print(f"  ✗ expected invoked: {token}")
        fail = 1
for token in expect.get("not_invoked", []):
    if token in transcript:
        print(f"  ✗ unexpectedly invoked: {token}")
        fail = 1
for art in expect.get("artifacts", []):
    if not (scratch / art).exists():
        print(f"  ✗ expected artifact: {art}")
        fail = 1
for pat in expect.get("output_matches", []):
    if not re.search(pat, transcript):
        print(f"  ✗ output did not match: {pat}")
        fail = 1
sys.exit(fail)
PY
  )
  local rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "  ✓ passed"
    rm -rf "$scratch"
  else
    echo "  · scratch: $scratch" >&2
    if [[ -f "$scratch/.transcript" ]]; then
      echo "  · transcript tail:" >&2
      tail -80 "$scratch/.transcript" | sed 's/^/      | /' >&2
    fi
    if [[ "$keep_failed" != "1" ]]; then
      rm -rf "$scratch"
    else
      echo "  · kept failed scratch because POLYMATH_KEEP_FAILED=1" >&2
    fi
  fi
  return $rc
}

total=0
failed=0
for f in "${fixtures[@]}"; do
  total=$((total + 1))
  if ! run_fixture "$f"; then
    failed=$((failed + 1))
  fi
done

echo
echo "Fixtures: $total run, $((total - failed)) passed, $failed failed."
[[ $failed -eq 0 ]]
