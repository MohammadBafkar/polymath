#!/usr/bin/env bash
# polymath-connector-sentry UserPromptSubmit hook
#
# When the prompt mentions a Sentry issue URL (sentry.io / self-hosted) or
# an issue short ID (PROJECT-NNNN with leading PROJECT being a Sentry slug,
# typically lowercase + dashes), hint the model to fetch via the sentry MCP.
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

# Sentry issue URL shapes:
#   https://<org>.sentry.io/issues/<numeric-id>/
#   https://sentry.io/organizations/<org>/issues/<numeric-id>/
#   https://<self-hosted-domain>/organizations/<org>/issues/<numeric-id>/
urls="$(printf '%s' "$prompt" | grep -oE 'https://[A-Za-z0-9.-]+/(organizations/[A-Za-z0-9_-]+/issues|issues)/[0-9]+' | sort -u | head -3 || true)"

# Sentry short IDs look like "PROJECT-123" but conflict with Jira keys.
# Match only when the prompt explicitly says "Sentry" near the ID to avoid
# false positives on Jira keys.
short_ids=""
if printf '%s' "$prompt" | grep -qi "sentry"; then
  short_ids="$(printf '%s' "$prompt" | grep -oE '\b[a-z][a-z0-9-]{2,15}-[0-9]+\b' | sort -u | head -3 || true)"
fi

[[ -z "$urls" && -z "$short_ids" ]] && exit 0

echo "[polymath-connector-sentry] Sentry reference(s) detected:"
[[ -n "$urls" ]]      && printf '  - %s\n' $urls
[[ -n "$short_ids" ]] && printf '  - %s (Sentry short ID; verify against Jira)\n' $short_ids
echo "Hint: fetch via the \`sentry\` MCP server — get_issue, list_events,"
echo "      get_event (full stack trace + breadcrumbs)."
