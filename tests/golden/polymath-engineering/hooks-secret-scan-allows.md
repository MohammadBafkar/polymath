---
plugin: polymath-engineering
scenario: hooks-secret-scan-allows
expect:
  invoked: []
  output_matches: []
  not_invoked: []
timeout_seconds: 30
---

# Prompt

> Invoke the PreToolUse(Write|Edit) secret-scan hook with a benign
> payload that contains no recognised secret pattern. Confirm the hook
> exits 0 with no stdout/stderr surface.

# Setup

```bash
payload='{"tool":"Edit","input":{"file_path":"src/util.py","new_string":"def add(a, b):\n    return a + b"}}'
```

# Run

```bash
echo "$payload" | plugins/polymath-engineering/hooks/scripts/secret-scan.sh
rc=$?
```

# Acceptance

- `rc` is `0`.
- Stdout is empty.
- Stderr is empty.
- The hook MUST NOT emit a heuristic warning for benign payloads
  (precision-favored discipline — no broad pattern like the word
  "password" alone).

# Why this fixture exists

This is the necessary partner to `hooks-secret-scan-blocks.md`. A
hook that blocks everything has 100% recall but 0% utility. The
precision-favored discipline in the script (specific token shapes
like `ghp_<36>`, `AKIA<16>`, PEM headers, `sk-ant-`, `sk-`) is what
makes the scanner usable in practice. This fixture asserts that
discipline survives every refactor.
