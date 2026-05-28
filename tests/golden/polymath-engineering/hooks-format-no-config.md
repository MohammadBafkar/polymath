---
plugin: polymath-engineering
scenario: hooks-format-no-config
expect:
  invoked: []
  output_matches: []
  not_invoked: []
timeout_seconds: 30
---

# Prompt

> Invoke the PostToolUse(Write|Edit) formatter hook in a directory
> that has *no* formatter config (no biome.json, no prettier config,
> no pyproject.toml, no ruff.toml, no rustfmt.toml). Confirm the hook
> exits 0 without running any formatter.

# Setup

```bash
scratch="$(mktemp -d)"
cd "$scratch"
# Intentionally NO config file is created.
payload='{"tool":"Edit","input":{"file_path":"'"$scratch"'/src/x.py","new_string":"x = 1"}}'
```

# Run

```bash
echo "$payload" | plugins/polymath-engineering/hooks/scripts/format-if-config.sh
rc=$?
```

# Acceptance

- `rc` is `0`.
- The formatter was NOT invoked (stdout/stderr empty or trace shows the
  config-detection step exited "no config found").
- No new files appear in the scratch directory.

# Why this fixture exists

The formatter hook's safety rail is "never format without a config" —
formatting a file that the project hasn't opted into formatting causes
unwanted diffs and surprises the user. A regression (e.g. defaulting to
biome when no config is found) would silently rewrite source on every
Edit. This fixture is the falsifiability anchor for that rail.
