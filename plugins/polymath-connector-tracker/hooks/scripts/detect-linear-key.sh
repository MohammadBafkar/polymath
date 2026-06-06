#!/usr/bin/env bash
# polymath-connector-tracker UserPromptSubmit hook (Linear detection)
#
# When the prompt contains a Linear-shape issue key (TEAM-NNN) AND mentions
# "Linear" nearby (to disambiguate from Jira), hint at fetching via the
# linear MCP. Also catch full linear.app URLs.
set -euo pipefail

payload="$(cat)"

prompt="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("prompt",""))
except Exception:
    pass
' 2>/dev/null || true)"

[[ -z "$prompt" ]] && exit 0

urls="$(printf '%s' "$prompt" | grep -oE 'https://linear\.app/[A-Za-z0-9_-]+/issue/[A-Z][A-Z0-9_]+-[0-9]+' | sort -u | head -3 || true)"

# Linear keys look like TEAM-123, identical to Jira. Only match when the
# prompt explicitly references Linear (case-insensitive). Use the same
# vendor-ID exclusion list as the Jira hook to be safe.
keys=""
if printf '%s' "$prompt" | grep -qi "linear"; then
  keys="$(printf '%s' "$prompt" | python3 -c '
import re, sys
EXCLUDE = {"CVE","GHSA","RHSA","USN","CWE","CAN","CNNVD","BDU"}
out = []
for m in re.finditer(r"(?<![A-Z0-9-])\b([A-Z][A-Z0-9_]{1,5})-([0-9]+)\b", sys.stdin.read()):
    proj, num = m.group(1), m.group(2)
    if proj in EXCLUDE:
        continue
    out.append(f"{proj}-{num}")
print("\n".join(sorted(set(out))))
' | head -5)"
fi

[[ -z "$urls" && -z "$keys" ]] && exit 0

echo "[polymath-connector-tracker] Linear reference(s) detected:"
[[ -n "$urls" ]] && printf '  - %s\n' $urls
[[ -n "$keys" ]] && printf '  - %s\n' $keys
echo "Hint: fetch via the \`linear\` MCP server — issue.get, issue.list,"
echo "      issue.update, comment.create, cycle.get."
