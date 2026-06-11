---
plugin: polymath-pipeline
scenario: enforce-gate-deny-then-mark
expect:
  invoked: []
  output_matches:
    - "polymath-pipeline enforce"
    - "marked"
  not_invoked: []
timeout_seconds: 30
---

# Prompt

> Run the polymath-pipeline enforce gate against a scratch repo that
> declares `routing.mode: enforce`. Confirm a mutating tool call is
> denied (exit 2), a read-only command is exempt, and `mark` opens the
> gate — the full classify-then-mutate loop.

# Setup

```bash
scratch="$(mktemp -d)"
export CLAUDE_PLUGIN_DATA="$scratch/.pdata"
mkdir -p "$scratch/repo/.polymath"
cd "$scratch/repo" && git init -q
cat > .polymath/project.yaml <<'YAML'
schemaVersion: 1
project:
  name: gate-demo
stack:
  languages:
    - lang: python
routing:
  mode: enforce
YAML
PIPE="plugins/polymath-pipeline/bin/polymath-pipeline"   # marketplace checkout path
```

# Run

```bash
# 1. Read-only Bash is exempt (exit 0).
echo '{"session_id":"fx","cwd":"'$scratch'/repo","tool_name":"Bash","tool_input":{"command":"git status --short"}}' \
  | "$PIPE" hook-pretool; echo "readonly_exit=$?"

# 2. Mutating Bash is denied (exit 2, reason on stderr).
echo '{"session_id":"fx","cwd":"'$scratch'/repo","tool_name":"Bash","tool_input":{"command":"echo done > status.txt"}}' \
  | "$PIPE" hook-pretool; echo "deny_exit=$?"

# 3. Classify + mark, then the same call is allowed (exit 0).
(cd "$scratch/repo" && "$PIPE" mark --surface direct)
echo '{"session_id":"fx","cwd":"'$scratch'/repo","tool_name":"Bash","tool_input":{"command":"echo done > status.txt"}}' \
  | "$PIPE" hook-pretool; echo "allow_exit=$?"
```

# Acceptance

- Step 1 prints `readonly_exit=0` — the modify-pattern blacklist exempts
  read-only commands.
- Step 2 prints `deny_exit=2` and stderr contains
  `polymath-pipeline enforce` with the mark instruction; the decision log
  (`$CLAUDE_PLUGIN_DATA/decisions.jsonl`) gains an `enforce-deny` event.
- Step 3's `mark` prints `"marked": true` and the retried call prints
  `allow_exit=0`; the log gains a `classified` event.
- `POLYMATH_PIPELINE_OFF=1` on any step allows the call and logs a
  `kill-switch` event — never silent.

# Why this fixture exists

The enforce gate is the only Polymath surface that can BLOCK a tool
call, so its failure modes are asymmetric: too eager and it bricks
opted-in repos; too lax and `routing.mode: enforce` is a no-op nobody
notices. This fixture pins the deny → mark → allow loop and the audited
escape hatches end-to-end through the real hook entrypoint.
