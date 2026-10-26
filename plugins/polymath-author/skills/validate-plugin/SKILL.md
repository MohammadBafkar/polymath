---
name: validate-plugin
description: Run every Polymath gate against one plugin — conformance, claude plugin validate, lint-skills, token budget, workflow schema.
---

# validate-plugin

> Run every gate the marketplace requires. Output is a pass/fail per gate with the failing line cited.

## When to use

- A new plugin is being added; need to know if it's submission-ready.
- An existing plugin was edited and you want to verify nothing broke.
- A workflow's pre-merge step needs the gate report.

## Inputs

- Path to the plugin (default: cwd if it's a `plugins/<name>/` directory).
- Must run from a Polymath marketplace checkout (the directory with `.claude-plugin/marketplace.json`) — the gates live in its `tools/`. If there is none, say so and stop.

## Procedure

1. **Single-plugin conformance — the source of truth.** `tools/conformance.sh plugins/polymath-<name>`. It runs the MANIFEST/SKILL/TEMPLATE/WORKFLOW/FIXTURE/DOCS checks for that plugin (and `claude plugin validate --strict` when the CLI is on PATH). Every other step below adds detail or catches what this misses; it never replaces it.
2. **Manifest validation** — `claude plugin validate --strict <path>`. Surface every error and warning; skip with `N/A (claude CLI not installed)` rather than reporting a pass.
3. **Skill lint** — `tools/lint-skills.sh`: description ≤ 200 chars, SKILL.md ≤ 500 lines, and the output-shape ratchet (`registry/output-shape-baseline.txt`).
4. **Token budget** — `tools/token-report.py budget` for the heuristic; when the CLI is available, `claude --plugin-dir <path> plugin details <name>` for the canonical per-component cost. Per-plugin cap is 400 tok (heuristic); flag if over.
5. **Workflow schema** — if the plugin ships any `workflows/*.yaml`, run `plugins/polymath-flows/bin/polymath-flow validate <file>` on each, then `tools/build-workflow-index.py --check`.
6. **Index drift** — if the plugin has `routing.yaml` sidecars run `tools/build-surface-index.py --check`; if it has `bindings/`, run `tools/build-capability-index.py --check`.
7. **Frontmatter** — every SKILL.md, command.md, and agent.md has `name` (agents: equal to the file stem) and `description`; descriptions lead with an imperative verb. No command shares its name with a skill in the same plugin (the skill is already `/plugin:skill`).

## Output

```text
Validate: plugins/polymath-foo

  ✓ conformance.sh plugins/polymath-foo  passed (MANIFEST, SKILL, TEMPLATE, FIXTURE, DOCS)
  ✓ claude plugin validate --strict      passed
  ✓ lint-skills.sh                       passed (3 SKILL.md, 2 commands)
  ✓ token-report.py budget               heuristic 142 tok (under 400 cap)
  ✓ claude plugin details                canonical 218 tok always-on
  ✓ workflow schema                      n/a (no workflows in plugin)
  ✓ index drift                          surface + capability indexes in sync
  ✓ frontmatter discipline               all components have name + description

Result: PASS. Ready for submission to polymath marketplace.
```

If any gate fails, the report lists the failing file:line and the corrective change.

## Quality bar

- Every gate produces a binary pass/fail (or an explicit N/A with the reason) + a one-line evidence excerpt.
- A gate that could not run is never reported as passed.
- Failure produces a concrete fix recommendation.
