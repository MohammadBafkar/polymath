---
plugin: polymath-engineering
scenario: hooks-secret-scan-blocks
expect:
  invoked: []
  output_matches:
    - "BLOCKED"
  not_invoked: []
timeout_seconds: 30
---

# Prompt

> Invoke the PreToolUse(Write|Edit) secret-scan hook directly with a
> payload containing a literal GitHub personal-access token. Confirm
> the hook blocks (exit 2) and surfaces a BLOCKED message on stderr.

# Setup

```bash
payload='{"tool":"Edit","input":{"file_path":"src/config.py","new_string":"GH_TOKEN = \"ghp_'"$(printf 'A%.0s' $(seq 1 36))"'\""}}'
```

# Run

```bash
echo "$payload" | plugins/polymath-engineering/hooks/scripts/secret-scan.sh
rc=$?
```

# Acceptance

- `rc` is `2` (the hook exit code that blocks the tool call).
- Stderr contains the literal word `BLOCKED`.
- The blocked-reason message names the pattern that matched (e.g.
  `GitHub personal access token`).
- A benign payload (e.g. `GH_TOKEN = "see-environment-variable"`)
  produces exit `0` with silent stdout.

# Why this fixture exists

The secret-scan hook is the catalog's hardest-running safety surface —
it fires on every `Write` or `Edit` invocation. A silent regression
(bash version drift, payload format change, regex compilation failure)
would let real secrets sail through into commits. This fixture is the
falsifiability anchor: the day it stops blocking is the day a regression
has shipped.
