#!/usr/bin/env bash
# polymath-engineering PreToolUse(Write|Edit) hook
#
# Reads the tool-input payload from stdin and inspects the `content` for common
# secret patterns. Exits 2 (block) if a likely secret is found; otherwise exits
# 0. The block reason is printed to stdout so the model and user can see it.
set -euo pipefail

payload="$(cat)"

content="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    args = data.get("tool_input", {}) or {}
    for key in ("content", "new_string"):
        v = args.get(key)
        if v:
            print(v)
            sys.exit(0)
except Exception:
    pass
' 2>/dev/null || true)"

if [[ -z "$content" ]]; then
  exit 0
fi

block() {
  local reason="$1"
  printf 'polymath-engineering secret-scan: BLOCKED — %s\n' "$reason"
  exit 2
}

# Patterns lifted from common scanners. Conservative; favors precision over recall
# so the hook does not become noise.
while IFS= read -r line; do
  case "$line" in
    *"AKIA"*) [[ "$line" =~ AKIA[0-9A-Z]{16} ]] && block "looks like an AWS access key" ;;
    *"aws_secret_access_key"*) [[ "$line" =~ aws_secret_access_key[[:space:]]*=[[:space:]]*[A-Za-z0-9/+=]{40,} ]] && block "looks like an AWS secret key" ;;
    *"-----BEGIN "*"PRIVATE KEY"*) block "PEM private key in content" ;;
    *"ghp_"*) [[ "$line" =~ ghp_[A-Za-z0-9]{36,} ]] && block "looks like a GitHub personal access token" ;;
    *"github_pat_"*) [[ "$line" =~ github_pat_[A-Za-z0-9_]{40,} ]] && block "looks like a GitHub fine-grained token" ;;
    *"xoxb-"*|*"xoxp-"*|*"xoxa-"*) block "looks like a Slack token" ;;
    *"sk-ant-"*) [[ "$line" =~ sk-ant-[A-Za-z0-9_-]{20,} ]] && block "looks like an Anthropic API key" ;;
    *"sk-"*) [[ "$line" =~ sk-[A-Za-z0-9]{32,} ]] && block "looks like an OpenAI-style API key" ;;
  esac
done <<< "$content"

exit 0
