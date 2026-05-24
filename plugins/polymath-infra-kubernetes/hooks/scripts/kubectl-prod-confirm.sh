#!/usr/bin/env bash
# polymath-infra-kubernetes PreToolUse(Bash) hook
#
# Blocks mutating kubectl commands (`apply`, `delete`, `patch`, `replace`,
# `scale`, `rollout`, `cordon`, `drain`) when the current kube-context name
# looks like production. The user can override per-call by including the
# string "POLYMATH_ACK_PROD" anywhere in the command — that's the explicit
# confirmation channel.
#
# Reads the tool-input payload from stdin. Exits:
#   0 — allow.
#   2 — block with reason printed to stdout (model + user see it).
set -euo pipefail

payload="$(cat)"

cmd="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    args = data.get("tool_input", {}) or {}
    print(args.get("command", ""))
except Exception:
    pass
' 2>/dev/null || true)"

# Only care about kubectl invocations.
case "$cmd" in
  *kubectl* ) ;;
  * ) exit 0 ;;
esac

# Only care about mutating verbs.
is_mutating=0
for verb in apply delete patch replace scale "rollout " cordon drain edit; do
  case "$cmd" in
    *"kubectl $verb"*|*"kubectl  $verb"*) is_mutating=1; break ;;
  esac
done
[[ "$is_mutating" -eq 0 ]] && exit 0

# If the model already acknowledged, allow.
case "$cmd" in
  *"POLYMATH_ACK_PROD"*) exit 0 ;;
esac

# Resolve the current context. Tolerate kubectl missing — if we can't
# detect a context, we don't block (false positives on dev shells are worse
# than letting a known-dev command through).
if ! command -v kubectl >/dev/null 2>&1; then
  exit 0
fi
ctx="$(kubectl config current-context 2>/dev/null || true)"
[[ -z "$ctx" ]] && exit 0

# Production heuristic: context name contains "prod", or matches the
# operator-provided regex via POLYMATH_K8S_PROD_PATTERN.
pattern="${POLYMATH_K8S_PROD_PATTERN:-prod}"
if echo "$ctx" | grep -Eiq "$pattern"; then
  cat >&2 <<EOF
polymath-infra-kubernetes: BLOCKED — kubectl mutating verb against a
production-looking context.

  Current kube-context: $ctx
  Detected match:       /$pattern/i
  Command:              $cmd

To proceed, re-issue the command including the literal token
POLYMATH_ACK_PROD anywhere (e.g. in a trailing comment):

  $cmd  # POLYMATH_ACK_PROD

Or set POLYMATH_K8S_PROD_PATTERN to a regex that excludes this context.
EOF
  exit 2
fi

exit 0
