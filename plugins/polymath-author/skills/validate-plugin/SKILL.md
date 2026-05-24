---
name: validate-plugin
description: Run every Polymath gate against a plugin — claude plugin validate, lint-skills, token-budget, workflow schema.
---

# validate-plugin

> Run every gate the marketplace requires. Output is a pass/fail per gate with the failing line cited.

## When to use

- A new plugin is being added; need to know if it's submission-ready.
- An existing plugin was edited and you want to verify nothing broke.
- A workflow's pre-merge step needs the gate report.

## Inputs

- Path to the plugin (default: cwd if it's a `plugins/<name>/` directory).

## Procedure

1. **Manifest validation** — `claude plugin validate --strict <path>` from the plugin directory. Surface every error and warning.
2. **Skill lint** — `tools/lint-skills.sh`. Description ≤ 200 chars, SKILL.md ≤ 500 lines.
3. **Token budget** — `tools/token-budget.sh` for the heuristic, then `claude plugin details <name>@polymath` for the canonical measurement. Per-plugin cap is 400 tok; flag if over.
4. **Template materialization** — if `.claude-plugin/templates.json` exists, `tools/link-templates.sh` must materialize every named template without error.
5. **Workflow schema** — if the plugin ships any `workflows/*.yaml`, run `plugins/polymath-flows/bin/polymath-flow validate <file>` on each.
6. **Frontmatter** — every SKILL.md, command.md, and agent.md has the required frontmatter fields (`name`, `description`); descriptions lead with an imperative verb.

## Output

```text
Validate: plugins/polymath-foo

  ✓ claude plugin validate --strict      passed
  ✓ lint-skills.sh                       passed (3 SKILL.md, 2 commands)
  ✓ token-budget.sh                      heuristic 142 tok
  ✓ claude plugin details                canonical 218 tok (under 400 cap)
  ✓ link-templates.sh                    materialized 2 templates
  ✓ workflow schema                      n/a (no workflows in plugin)
  ✓ frontmatter discipline               all components have name + description

Result: PASS. Ready for submission to polymath marketplace.
```

If any gate fails, the report lists the failing file:line and the corrective change.

## Quality bar

- Every gate produces a binary pass/fail + a one-line evidence excerpt.
- No "looks good to me" findings.
- Failure produces a concrete fix recommendation.
