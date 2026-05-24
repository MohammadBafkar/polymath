#!/usr/bin/env bash
# polymath-connector-pagerduty UserPromptSubmit hook
#
# When the prompt mentions a PagerDuty incident URL or an incident ID
# (e.g. PT12345 or PD-INC-...), hint the model to fetch via the pagerduty MCP.
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

urls="$(printf '%s' "$prompt" | grep -oE 'https://[A-Za-z0-9.-]+\.pagerduty\.com/incidents/[A-Z0-9]+' | sort -u | head -3 || true)"
ids="$(printf '%s' "$prompt" | grep -oE '\b(P[A-Z0-9]{6,}|PD-INC-[A-Z0-9-]+)\b' | sort -u | head -5 || true)"

[[ -z "$urls" && -z "$ids" ]] && exit 0

echo "[polymath-connector-pagerduty] PagerDuty reference(s) detected:"
[[ -n "$urls" ]] && printf '  - %s\n' $urls
[[ -n "$ids"  ]] && printf '  - %s\n' $ids
echo "Hint: fetch via the \`pagerduty\` MCP — get_incident, list_log_entries,"
echo "      get_oncall_for_service, list_notes."
