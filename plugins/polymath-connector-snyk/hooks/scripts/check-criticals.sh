#!/usr/bin/env bash
# polymath-connector-snyk Stop hook
#
# At end-of-turn, if the project has a Snyk-known manifest (package.json,
# pyproject.toml, go.mod, etc.) AND the `snyk` CLI is installed AND
# authenticated AND there's a cached recent test result with criticals,
# emit a single-line nudge. Quiet otherwise.
set -euo pipefail

cwd="$(pwd)"

# Snyk needs the CLI. If it isn't installed, no-op.
command -v snyk >/dev/null 2>&1 || exit 0

# Detect a manifest the CLI knows about.
has_manifest=0
for f in package.json pyproject.toml requirements.txt go.mod pom.xml Gemfile composer.json; do
  if [[ -f "$cwd/$f" ]]; then
    has_manifest=1
    break
  fi
done
[[ "$has_manifest" -eq 0 ]] && exit 0

# Only act if Snyk CLI is authed (avoid prompting login mid-session).
snyk config get api >/dev/null 2>&1 || exit 0

# Look for a recent cached snyk test result (~/.config/configstore or .snyk).
# Skip the network call from a hook — too slow. Surface only if a local file
# tells us there are open criticals.
cache="$cwd/.snyk.last.json"
[[ ! -f "$cache" ]] && exit 0

criticals="$(python3 -c "
import json, sys
try:
    data = json.load(open(sys.argv[1]))
    if isinstance(data, dict):
        vulns = data.get('vulnerabilities', []) or []
    elif isinstance(data, list):
        vulns = data
    else:
        vulns = []
    print(sum(1 for v in vulns if (v.get('severity') or '').lower() == 'critical'))
except Exception:
    pass
" "$cache" 2>/dev/null || echo 0)"

if [[ -n "$criticals" && "$criticals" -gt 0 ]]; then
  echo "[polymath-connector-snyk] $criticals open critical vulnerability(ies) in this project (per cached snyk test). Consider re-running \`snyk test\` or fetching via the snyk MCP before shipping."
fi

exit 0
