---
plugin: polymath-connector-snyk
scenario: hooks-warn-on-criticals
expect:
  invoked: []
  output_matches:
    - "Open critical"
  not_invoked: []
timeout_seconds: 30
---

# Prompt

> Invoke the Stop hook from polymath-connector-snyk against a scratch
> branch state that simulates one open critical vulnerability finding.
> Confirm the hook surfaces a warning before the session ends.

# Setup

```bash
scratch="$(mktemp -d)"
cd "$scratch"
git init -q
git config user.email "ci@polymath.test"
git config user.name "polymath-ci"
echo "# scratch" > README.md
git add . && git commit -q -m "init"
# Simulate a recorded Snyk scan with one open critical finding.
mkdir -p .polymath/snyk
cat > .polymath/snyk/findings.json <<'JSON'
{
  "branch": "main",
  "findings": [
    {"id": "SNYK-JS-LODASH-1234", "severity": "critical", "status": "open"}
  ]
}
JSON
```

# Run

```bash
plugins/polymath-connector-snyk/hooks/scripts/check-criticals.sh
rc=$?
```

# Acceptance

- `rc` is `0` (Stop hooks warn, they don't fail-close).
- Stdout contains the literal phrase `Open critical` (case sensitive)
  alongside the finding identifier `SNYK-JS-LODASH-1234`.
- When the scratch directory has no findings file, the hook exits 0
  silently — the warning surface is conditional on real findings.

# Why this fixture exists

The plugin description claims the Stop hook "warns if the current
branch has open critical vulns" — this fixture is the falsifiability
anchor for that claim. The day it stops surfacing the open critical
is the day the Stop hook has regressed.
