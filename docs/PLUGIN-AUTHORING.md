# Plugin authoring guide

How to create, structure, and submit a Polymath plugin. See
[`docs/WORKFLOW-SCHEMA.md`](WORKFLOW-SCHEMA.md) for the workflow YAML
schema.

## 1. Component decision matrix

| Need                                                              | Component                            |
| ----------------------------------------------------------------- | ------------------------------------ |
| Event-driven gate (block secrets, format on save, push reminder)  | Hook                                 |
| External service tool calls (GitHub, Jira, Datadog, …)            | MCP server                           |
| Persistent background watcher (logs, CI, deploy status)           | Monitor                              |
| Per-language code intelligence                                    | Defer to official LSP / external skill catalog |
| Specialist isolated context (deep audit, panel critique, research) | Agent                                |
| Quick alias / flow orchestrator / no supporting files             | Command (flat `.md` in `commands/`)  |
| Procedure with templates, scripts, examples, or references        | Skill (directory with `SKILL.md`)    |

Polymath does not ship output styles — tone control lives in
reference-content skills (e.g. `polymath-writing:editorial-pass`).

## 2. Plugin layout

```text
plugins/polymath-<name>/
├── .claude-plugin/
│   └── plugin.json
├── skills/<skill>/
│   ├── SKILL.md
│   ├── references/             # optional
│   └── scripts/                # optional
├── templates/                  # plugin-owned artifact templates (PRD.md, etc.)
├── commands/<cmd>.md
├── agents/<role>.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
├── monitors/monitors.json      # rare
├── .mcp.json                   # connector plugins only
├── workflows/*.yaml            # polymath-flows only
├── bin/                        # bundled executables (optional)
├── tests/
├── README.md
└── CHANGELOG.md
```

## 3. plugin.json

```jsonc
{
  "name": "polymath-thing",
  "version": "0.1.0",
  "description": "Short, ≤ 200 chars, trigger phrase first.",
  "license": "Apache-2.0",
  "dependencies": {
    "plugins": ["polymath-core"]
  },
  "metadata": {
    "category": "engineering",
    "tags": ["tdd", "review"]
  }
}
```

Do **not** add unknown top-level fields (including `status`). Claude
Code's `plugin validate --strict` treats unknown fields as warnings,
and conformance runs the validator with `--strict`. Plugin-level
metadata that doesn't fit the official manifest schema lives in
`.claude-plugin/marketplace.json` — see § 3.1.

## 3.1 Maturity tier (`status`)

Every plugin declares a maturity tier in `marketplace.json`. The
canonical definitions and promotion bars live in
[`docs/MATURITY.md`](MATURITY.md) — read that file when deciding what
to set on a new plugin or what to bump it to. The short table:

| Tier | One-liner |
| --- | --- |
| `experimental` | Scaffolded; default for new plugins. |
| `beta` | Structurally proven on disk (skill bakeoff + triggering tests, OR foundation-runner with ≥ 20 unit-test assertions + an end-to-end job). |
| `stable` | Live bakeoff ≥ 8 / delta ≥ 2 + at least one external adopter. No plugin in the catalog is `stable` today. |
| `deprecated` | Replacement and removal date named in `README.md`. |

`tools/conformance.sh MANIFEST-3` rejects a plugin whose
`marketplace.json` entry is missing `status` or sets it to an unknown
value.

Add the entry in `marketplace.json`:

```jsonc
{
  "name": "polymath-thing",
  "source": "./plugins/polymath-thing",
  "description": "…",
  "version": "0.1.0",
  "category": "engineering",
  "tags": ["tdd", "review"],
  "status": "experimental"
}
```

`tools/conformance.sh` rejects a plugin whose `marketplace.json`
entry is missing `status` or sets it to an unknown value.

## 4. Skill frontmatter rules

- `name`: bare kebab-case slug.
- `description`: ≤ 200 chars, trigger phrase first, present tense.
- `SKILL.md` body ≤ 500 lines. Spill to `references/`.
- Reference the plugin's templates via relative path from the skill
  (e.g. `[\`PRD.md\`](../../templates/PRD.md)`).

Example:

```markdown
---
name: prd
description: Draft a PRD from a problem statement plus user/context inputs; populates docs/prds/<slug>.md.
---

# prd

## When to use

- The user says "draft a PRD" or "we need a spec for X".
- A workflow step invokes `polymath-product:prd`.

## Procedure

1. …
```

## 5. Commands vs skills

Both produce `/name` invocations. Choose by directory shape:

- **Command** (`commands/foo.md`): single flat file, ≤ 20 lines,
  ideal for aliases.
- **Skill** (`skills/foo/SKILL.md`): directory, bundles templates,
  scripts, references.

If both exist for the same name, the command must be a thin alias
pointing to the skill; the skill holds canonical content.

## 6. Agent rules

Agents are reserved for:

- Panels of critics running in parallel.
- Heavy research / audit that would flood the main context.
- Distinct named roles the user explicitly addresses.

Three structural constraints (verify against current Claude Code
docs before relying):

1. Plugin-shipped subagents **cannot** ship their own hooks, MCPs,
   or `permissionMode`.
2. Subagents **cannot** spawn subagents.
3. Subagent execution is synchronous from the caller's view.

A new agent ships with a golden fixture showing the forked-context
agent surfaces something a same-input no-agent baseline misses. The
baseline is the same input handed to the same Claude lead without
any subagent. The question an agent answers is *"does forking context
catch something the same lead misses without it?"* Both traces are
checked in and reviewed together.

## 7. Hooks

- `PreToolUse(Write|Edit)` for secret-scan or format checks.
- `PostToolUse(Edit|Write)` for formatter or lint runs.
- `SessionStart` for printing active plugins or paused workflows.
- `Stop` for end-of-turn nudges.

Hooks live in `hooks/hooks.json`; helper scripts live in
`hooks/scripts/`.

## 8. Token-budget discipline

- Per-plugin always-on listing ≤ 400 tokens.
- Catalog total target scales with plugin count (see
  `tools/token-budget.sh`).
- Run `tools/token-budget.sh` locally before PR.

CI fails ≥ 50-token regressions without an explicit `expected-cost:`
override.

## 9. Templates

Each plugin owns its artifact templates under
`plugins/<plugin>/templates/`. Skills reference templates by relative
path; workflows validate the frontmatter via `mustPass: artifactValid`
or `artifactSchemaStrict` against the matching JSON schema in
`shared/schemas/artifacts/`.

Canonical artifact schemas the catalog enforces today:

- `PRD`, `ADR`, `Plan`, `RFC`, `Runbook`, `ArchitectureDoc`,
  `DACIDecision`, `TradeoffMatrix`, `Postmortem`, `ThreatModel`,
  `PRDescription`.

Run `tools/conformance.sh <plugin>` to check that template +
frontmatter + schema agree.

## 10. Tests

Each plugin should ship at least one golden fixture under
`tests/golden/<plugin>/<scenario>.md`. Fixtures contain a goal prompt
plus expected component invocations. CI runs `claude -p` against
these when `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) is
configured.

A plugin may additionally ship:

- **Bakeoff cases** under `tests/bakeoff/<plugin>/<scenario>/case.json`
  comparing baseline Claude Code against Polymath with regex +
  optional LLM-judge scoring.
- **Skill-triggering tests** under
  `tests/skill-triggering/<plugin>/<skill>.md` asserting the right
  Skill tool-use happens for naive user prompts.

## 11. Submitting a plugin

1. `polymath-author:new-plugin <name>` (or
   `plugins/polymath-author/bin/new-plugin.sh <name>`) to scaffold.
2. Author components.
3. `tools/validate-all.sh && tools/lint-skills.sh && tools/token-budget.sh`
   must pass.
4. Add at least one golden fixture under `tests/golden/<plugin>/`.
5. Register the plugin in `.claude-plugin/marketplace.json`.
6. Open a PR. CI runs all gates.
