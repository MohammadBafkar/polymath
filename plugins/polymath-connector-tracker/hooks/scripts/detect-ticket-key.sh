#!/usr/bin/env bash
# polymath-connector-tracker UserPromptSubmit hook (Jira detection)
#
# When the user's prompt contains a Jira issue key (PROJ-123 shape) or an
# Atlassian browse URL, hint the model to fetch the issue via the jira MCP.
#
# Hint, not block. Exit 0 with stdout context.
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

# A Jira key is a short project prefix + dash + digits. Vendor IDs like
# SNYK-JS-LODASH-1234567 and CVE-2024-1234 must NOT match. We require:
#   - 2–6 uppercase chars before the dash,
#   - NOT preceded by another dash-separated uppercase token (handles vendor IDs),
#   - NOT a known non-Jira prefix (CVE, GHSA, RHSA, USN, CWE).
keys="$(printf '%s' "$prompt" | python3 -c '
import re, sys
text = sys.stdin.read()
EXCLUDE = {"CVE","GHSA","RHSA","USN","CWE","CAN","CNNVD","BDU"}
out = []
for m in re.finditer(r"(?<![A-Z0-9-])\b([A-Z][A-Z0-9_]{1,5})-([0-9]+)\b", text):
    proj, num = m.group(1), m.group(2)
    if proj in EXCLUDE:
        continue
    out.append(f"{proj}-{num}")
print("\n".join(sorted(set(out))))
' | head -5)"

# Also catch full browse URLs.
urls="$(printf '%s' "$prompt" | grep -oE 'https://[A-Za-z0-9.-]+\.atlassian\.net/browse/[A-Z][A-Z0-9_]+-[0-9]+' | sort -u | head -3 || true)"

[[ -z "$keys" && -z "$urls" ]] && exit 0

echo "[polymath-connector-tracker] Jira reference(s) detected:"
[[ -n "$keys" ]] && printf '  - %s\n' $keys
[[ -n "$urls" ]] && printf '  - %s\n' $urls
echo "Hint to assistant: fetch via the \`jira\` MCP server before responding."
echo "Useful tools: jira_get_issue, jira_search (JQL), jira_get_transitions."
