---
plugin: polymath-core
scenario: hooks-session-start-paused
expect:
  invoked: []
  output_matches:
    - "Polymath: 1 paused workflow"
    - "resume with /polymath-flows:resume-workflow"
  not_invoked: []
timeout_seconds: 30
---

# Prompt

> Run the polymath-core SessionStart hook against a scratch
> `${CLAUDE_PLUGIN_DATA}` containing one paused workflow run. Confirm
> the hook surfaces the paused run with a resume hint.

# Setup

```bash
scratch="$(mktemp -d)"
export CLAUDE_PLUGIN_DATA="$scratch"
mkdir -p "$scratch/polymath-flows/workflows/2026-05-28T12-00-shipFeature-rate-limit"
cat > "$scratch/polymath-flows/workflows/2026-05-28T12-00-shipFeature-rate-limit/state.json" <<'STATE'
{
  "run_id": "2026-05-28T12-00-shipFeature-rate-limit",
  "workflow": "shipFeature",
  "status": "paused",
  "pause_reason": "verify gate failed"
}
STATE
```

# Run

```bash
plugins/polymath-core/hooks/scripts/session-start.sh
```

# Acceptance

- Exit code is `0`.
- Standard output contains the line `Polymath: 1 paused workflow(s):`.
- The next line names `2026-05-28T12-00-shipFeature-rate-limit` and
  the resume hint `/polymath-flows:resume-workflow`.
- The script reads the legacy `${CLAUDE_PLUGIN_DATA}/workflows/` path
  as a fallback when `polymath-flows/workflows/` is absent (covered by
  the script's layout-fallback logic — assert by re-running the
  fixture against `mv $scratch/polymath-flows/workflows $scratch/workflows`).
- No errors emitted on stderr beyond the optional project-context
  loader summary (absent in this fixture's scratch dir).

# Why this fixture exists

This is the *falsifiability anchor* for polymath-core's SessionStart
hook. The hook fires on every Claude Code session; a silent regression
(env-var change, JSON format drift, layout move) would only surface
when a real user noticed paused workflows weren't appearing. The
fixture asserts the surface every release.
