# workflow-triggering tests

Falsification anchor for the workflow routing surface. Each test asserts that a
naive user prompt — one that does **not** name the workflow — makes the model
**propose** the right workflow under the detect → propose → confirm → run
contract documented in
[`run-workflow/SKILL.md`](../../plugins/polymath-flows/skills/run-workflow/SKILL.md).
This is the workflow analogue of [`../skill-triggering`](../skill-triggering).

## File shape

`tests/workflow-triggering/<workflow>.md`:

```markdown
---
workflow: reviewPlan
trigger_prompts:          # naive phrasings; must be a superset-or-equal of the
  - "review this plan"    # workflow YAML's own `triggers` (drift guard)
  - "poke holes in this plan"
  - "is this plan any good before I start"
must_propose:
  - reviewPlan
allow_propose:            # acceptable runner-ups on a genuine tie
  - deliberationLoop
forbidden_prompts:        # must propose NO workflow at all
  - "format my markdown"
---
```

## Running

```bash
python3 tools/workflow-triggering.py check   # frontmatter + drift guard (CI; no LLM)
python3 tools/workflow-triggering.py list     # one row per test
python3 tools/workflow-triggering.py run      # live; needs CLAUDE_CODE_OAUTH_TOKEN
```

`check` runs in `tools/conformance.sh --all` (the `WORKFLOW-TRIGGER` gate).
`run` is opt-in — it makes real model calls and is skipped when the `claude`
CLI is absent (e.g. fork PRs without secrets). At propose time the model emits a
one-line text proposal and stops, so `run` parses the assistant text for a
backticked workflow name (and also accepts an explicit `polymath-flow start`
call).
